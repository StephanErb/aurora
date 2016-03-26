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
