

TODO

(copy & paste dump below)


# Job Namespaces

Aurora allows for specifying an "environment" component in the job key, which essentially serves
as a namespace component . The values for "environment" are validated in the client and the scheduler
so as to allow any of "devel", "test", "production", and any value matching the regular expression
"staging[0-9]*".

None of the values imply any difference in the scheduling behavior. Conventionally, the
"environment" is set so as to indicate a certain level of stability in the behavior of the job
by ensuring that an appropriate level of testing has been performed on the application code. e.g.
in the case of a typical Job, releases may progress through the following phases in order of increasing level of stability: "devel", "test", "staging", "production".

Note that the differing expectation of stability, in the different environments, is primarily from the Jobs scheduled in the cluster, not from the Scheduler. Thus, the semantics of the "environment" chosen for a Job are purely defined by the Job Owner and affect the how the Job chooses to advertise differing levels of stability to its consumers. A given environment value is not indicative of a certain QoS expectation from the Scheduler.







# Oversubscription of Resources

**WARNING**: This feature is currently in alpha status. Do not use it in production clusters!

Mesos [supports a concept of revocable tasks](http://mesos.apache.org/documentation/latest/oversubscription/)
by oversubscribing machine resources by the amount deemed safe to not affect the existing
non-revocable tasks. Aurora now supports revocable jobs via a `tier` setting set to `revocable`
value.

The Aurora scheduler must be configured to receive revocable offers from Mesos and accept revocable
jobs. If not configured properly revocable tasks will never get assigned to hosts and will stay in
`PENDING`. Set these scheduler flag to allow receiving revocable Mesos offers:

    -receive_revocable_resources=true

Specify a tier configuration file path (unless you want to use the [default](../src/main/resources/org/apache/aurora/scheduler/tiers.json)):

    -tier_config=path/to/tiers/config.json


See the [Configuration Reference](references/configuration.md) for details on how to mark a job
as being revocable.





Production Quota & Preemption
=============================

In order to guarantee that important production jobs are always running, Aurora supports
preemption.

Under a particular resource shortage pressure, tasks from
[production](configuration-reference.md#job-objects) jobs may preempt tasks from any non-production
job. A production task may only be preempted by tasks from production jobs in the same role with
higher [priority](configuration-reference.md#job-objects).

Aurora requires resource quotas for
[production non-dedicated jobs](configuration-reference.md#job-objects). Quota is enforced at
the job role level and when set, defines a non-preemptible pool of compute resources within
that role. All job types (service, adhoc or cron) require role resource quota unless a job has
[dedicated constraint set](deploying-aurora-scheduler.md#dedicated-attribute).

To grant quota to a particular role in production, an operator can use the command
`aurora_admin set_quota`.
