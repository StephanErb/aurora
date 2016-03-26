## Introduction

Apache Aurora is a service scheduler that runs on top of Apache Mesos, enabling you to run long-running services and cron jobs that take advantage of Apache Mesos' scalability, fault-tolerance, and resource isolation.

We encourage you to ask questions on the [Aurora user list](http://aurora.apache.org/community/) or the `#aurora` IRC channel on `irc.freenode.net`.


## Getting Started

Information for everyone new to Apache Aurora.

 * [Aurora System Overview](getting-started/overview.md)
 * [Hello World Tutorial](getting-started/tutorial.md)
 * [Local cluster with Vagrant](getting-started/vagrant.md)
 * [Configuration Tutorial](getting-started/configuration-tutorial.md)

## Users
 * [Install Aurora on virtual machines on your private machine](vagrant.md)
 * [Hello World Tutorial](tutorial.md)
 * [User Guide](user-guide.md)
 * [Task Lifecycle](task-lifecycle.md)
 * [Configuration Tutorial](configuration-tutorial.md)
 * [Aurora + Thermos Reference](configuration-reference.md)
 * [Command Line Client](client-commands.md)
 * [Client cluster configuration](client-cluster-configuration.md)
 * [Cron Jobs](cron-jobs.md)


## Reference

The complete reference of commands and configuration options.


 * [Task lifecycle](reference/task-lifecycle.md)
 * Configuration (`.aurora` files)

    - [Coniguration Reference](reference/configuration-reference.md)
    - [Coniguration Best Practices](reference/configuration-best-bractices.md)
    - [Coniguration Templating](reference/configuration-templating.md)

 * Aurora Client

    - [Client Commands](reference/client-commands.md)
    - [Client Hooks](reference/client-hooks.md)
    - [Client Cluster Configuration](reference/client-cluster-configuration.md)


## Operators

For those that wish to manage and fine-tune an Aurora cluster.

 * [Installation](operations/installation.md)
 * [Configuration](operations/configuration.md)
 * [Monitoring](operations(monitoring.md)
 * [Security](operations/security.md)
 * [Storage](operations/storage.md)
 * [Backup](operations/backup-restore.md)


## Developers

All the information you need to start modifying Aurora and contributing back to the project:

 * [Contributing to the project](../CONTRIBUTING.md)
 * [Committer's Guide](development/committers-guide.md)
 * [Design Documents](design-documents.md)
 * Developing the Aurora components:

     - [Client](development/client.md)
     - [Scheduler](development/scheduler.md)
     - [Scheduler UI](development/ui.md)
     - [Thermos](development/client.md)
     - [Thrift structures](development/thrift.md)


## Additional Resources
 * [Tools integrating with Aurora](additional-resources/tools.md)
 * [Presentation videos and slides](additional-resources/presentations.md)
