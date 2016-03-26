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
