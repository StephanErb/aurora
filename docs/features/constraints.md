Scheduling Constraints
======================
TODO

(copy & paste dump below)

### Running stateful services
Aurora is best suited to run stateless applications, but it also accommodates for stateful services
like databases, or services that otherwise need to always run on the same machines.

#### Dedicated attribute
The Mesos slave has the `--attributes` command line argument which can be used to mark a slave with
static attributes (not to be confused with `--resources`, which are dynamic and accounted).

Aurora makes these attributes available for matching with scheduling
[constraints](configuration-reference.md#specifying-scheduling-constraints).  Most of these
constraints are arbitrary and available for custom use.  There is one exception, though: the
`dedicated` attribute.  Aurora treats this specially, and only allows matching jobs to run on these
machines, and will only schedule matching jobs on these machines.

See the [section](features/multitenancy.md) about resource quotas to learn how quotas apply to
dedicated jobs.

##### Syntax
The dedicated attribute has semantic meaning. The format is `$role(/.*)?`. When a job is created,
the scheduler requires that the `$role` component matches the `role` field in the job
configuration, and will reject the job creation otherwise.  The remainder of the attribute is
free-form. We've developed the idiom of formatting this attribute as `$role/$job`, but do not
enforce this. For example: a job `devcluster/www-data/prod/hello` with a dedicated constraint set as
`www-data/web.multi` will have its tasks scheduled only on Mesos slaves configured with:
`--attributes=dedicated:www-data/web.multi`.

A wildcard (`*`) may be used for the role portion of the dedicated attribute, which will allow any
owner to elect for a job to run on the host(s). For example: tasks from both
`devcluster/www-data/prod/hello` and `devcluster/vagrant/test/hello` with a dedicated constraint
formatted as `*/web.multi` will be scheduled only on Mesos slaves configured with
`--attributes=dedicated:*/web.multi`. This may be useful when assembling a virtual cluster of
machines sharing the same set of traits or requirements.

##### Example
Consider the following slave command line:

    mesos-slave --attributes="dedicated:db_team/redis" ...

And this job configuration:

    Service(
      name = 'redis',
      role = 'db_team',
      constraints = {
        'dedicated': 'db_team/redis'
      }
      ...
    )

The job configuration is indicating that it should only be scheduled on slaves with the attribute
`dedicated:db_team/redis`.  Additionally, Aurora will prevent any tasks that do _not_ have that
constraint from running on those slaves.




## Best practices
### Diversity
Data centers are often organized with hierarchical failure domains.  Common failure domains
include hosts, racks, rows, and PDUs.  If you have this information available, it is wise to tag
the mesos-slave with them as
[attributes](https://mesos.apache.org/documentation/attributes-resources/).

When it comes time to schedule jobs, Aurora will automatically spread them across the failure
domains as specified in the
[job configuration](configuration-reference.md#specifying-scheduling-constraints).

Note: in virtualized environments like EC2, the only attribute that usually makes sense for this
purpose is `host`.

