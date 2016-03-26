# Aurora Scheduler Storage

- [Overview](#overview)
- [Replicated Log Configuration](#replicated-log-configuration)
- [Backup Configuration](#replicated-log-configuration)
- [Storage Semantics](#storage-semantics)
  - [Reads, writes, modifications](#reads-writes-modifications)
    - [Read lifecycle](#read-lifecycle)
    - [Write lifecycle](#write-lifecycle)
  - [Atomicity, consistency and isolation](#atomicity-consistency-and-isolation)
  - [Population on restart](#population-on-restart)
  - [Population on restart](#population-on-restart)


## Overview

Aurora scheduler maintains data that need to be persisted to survive failovers and restarts.
For example:

* Task configurations and scheduled task instances
* Job update configurations and update progress
* Production resource quotas
* Mesos resource offer host attributes

Aurora solves its persistence needs by leveraging the Mesos implementation of a Paxos replicated
log [[1]](https://ramcloud.stanford.edu/~ongaro/userstudy/paxos.pdf)
[[2]](http://en.wikipedia.org/wiki/State_machine_replication) with a key-value
[LevelDB](https://github.com/google/leveldb) storage as persistence media.

Conceptually, it can be represented by the following major components:

* Volatile storage: in-memory cache of all available data. Implemented via in-memory
[H2 Database](http://www.h2database.com/html/main.html) and accessed via
[MyBatis](http://mybatis.github.io/mybatis-3/).
* Log manager: interface between Aurora storage and Mesos replicated log. The default schema format
is [thrift](https://github.com/apache/thrift). Data is stored in serialized binary form.
* Snapshot manager: all data is periodically persisted in Mesos replicated log in a single snapshot.
This helps establishing periodic recovery checkpoints and speeds up volatile storage recovery on
restart.
* Backup manager: as a precaution, snapshots are periodically written out into backup files.
This solves a [disaster recovery problem](operations/backup-restore.md)
in case of a complete loss or corruption of Mesos log files.

![Storage hierarchy](../images/storage_hierarchy.png)



## Replicated Log Configuration

Aurora schedulers use ZooKeeper to discover log replicas and elect a leader. Only one scheduler is
leader at a given time - the other schedulers follow log writes and prepare to take over as leader
but do not communicate with the Mesos master. Either 3 or 5 schedulers are recommended in a
production deployment depending on failure tolerance and they must have persistent storage.

Below is a summary of scheduler storage configuration flags that either don't have default values
or require attention before deploying in a production environment.

### `-native_log_quorum_size`
Defines the Mesos replicated log quorum size. In a cluster with `N` schedulers, the flag
`-native_log_quorum_size` should be set to `floor(N/2) + 1`. So in a cluster with 1 scheduler
it should be set to `1`, in a cluster with 3 it should be set to `2`, and in a cluster of 5 it
should be set to `3`.

  Number of schedulers (N) | ```-native_log_quorum_size``` setting (```floor(N/2) + 1```)
  ------------------------ | -------------------------------------------------------------
  1                        | 1
  3                        | 2
  5                        | 3
  7                        | 4

*Incorrectly setting this flag will cause data corruption to occur!*

### `-native_log_file_path`
Location of the Mesos replicated log files. Consider allocating a dedicated disk (preferably SSD)
for Mesos replicated log files to ensure optimal storage performance.

### `-native_log_zk_group_path`
ZooKeeper path used for Mesos replicated log quorum discovery.

See [code](../src/main/java/org/apache/aurora/scheduler/log/mesos/MesosLogStreamModule.java) for
other available Mesos replicated log configuration options and default values.

### Changing the Quorum Size
Special care needs to be taken when changing the size of the Aurora scheduler quorum.
Since Aurora uses a Mesos replicated log, similar steps need to be followed as when
[changing the mesos quorum size](http://mesos.apache.org/documentation/latest/operational-guide).

As a preparation, increase `-native_log_quorum_size` on each existing scheduler and restart them.
When updating from 3 to 5 schedulers, the quorum size would grow from 2 to 3.

When starting the new schedulers, use the `-native_log_quorum_size` set to the new value. Failing to
first increase the quorum size on running schedulers can in some cases result in corruption
or truncating of the replicated log used by Aurora. In that case, see the documentation on
[recovering from backup](operations/backup-restore.md).


## Backup Configuration

Configuration options for the Aurora scheduler backup manager.

### `-backup_interval`
The interval on which the scheduler writes local storage backups.  The default is every hour.

### `-backup_dir`
Directory to write backups to.

### `-max_saved_backups`
Maximum number of backups to retain before deleting the oldest backup(s).


## Storage Semantics

Implementation details of the Aurora storage system. Understanding those can sometimes be useful
when investigating performance issues.

### Reads, writes, modifications

All services in Aurora access data via a set of predefined store interfaces (aka stores) logically
grouped by the type of data they serve. Every interface defines a specific set of operations allowed
on the data thus abstracting out the storage access and the actual persistence implementation. The
latter is especially important in view of a general immutability of persisted data. With the Mesos
replicated log as the underlying persistence solution, data can be read and written easily but not
modified. All modifications are simulated by saving new versions of modified objects. This feature
and general performance considerations justify the existence of the volatile in-memory store.

#### Read lifecycle

There are two types of reads available in Aurora: consistent and weakly-consistent. The difference
is explained [below](#atomicity-and-isolation).

All reads are served from the volatile storage making reads generally cheap storage operations
from the performance standpoint. The majority of the volatile stores are represented by the
in-memory H2 database. This allows for rich schema definitions, queries and relationships that
key-value storage is unable to match.

#### Write lifecycle

Writes are more involved operations since in addition to updating the volatile store data has to be
appended to the replicated log. Data is not available for reads until fully ack-ed by both
replicated log and volatile storage.

### Atomicity, consistency and isolation

Aurora uses [write-ahead logging](http://en.wikipedia.org/wiki/Write-ahead_logging) to ensure
consistency between replicated and volatile storage. In Aurora, data is first written into the
replicated log and only then updated in the volatile store.

Aurora storage uses read-write locks to serialize data mutations and provide consistent view of the
available data. The available `Storage` interface exposes 3 major types of operations:
* `consistentRead` - access is locked using reader's lock and provides consistent view on read
* `weaklyConsistentRead` - access is lock-less. Delivers best contention performance but may result
in stale reads
* `write` - access is fully serialized by using writer's lock. Operation success requires both
volatile and replicated writes to succeed.

The consistency of the volatile store is enforced via H2 transactional isolation.

### Population on restart

Any time a scheduler restarts, it restores its volatile state from the most recent position recorded
in the replicated log by restoring the snapshot and replaying individual log entries on top to fully
recover the state up to the last write.
