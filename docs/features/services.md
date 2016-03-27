Services: Long running jobs
===========================

Services are differentiated from non-service Jobs in that they always restart on completion,
whether successful or unsuccessful. This is useful for long-running processes
such as webservices that should always be running, unless stopped explicitly.


Service Specification
---------------------

A job is identified as a service by the presence of the flag
``service=True` in the [`Job`](reference/configuration.md#job-objects) object.
The `Service` alias can be used as shorthand for `Job` with `service=True`.

Example (available in the [Vagrant environment](getting-started/vagrant.md)):

    $ cat /vagrant/examples/jobs/hello_world.aurora
    hello = Process(
      name = 'hello',
      cmdline = """
        while true; do
          echo hello world
          sleep 10
        done
      """)

    task = SequentialTask(
      processes = [hello],
      resources = Resources(cpu = 1.0, ram = 128*MB, disk = 128*MB)
    )

    jobs = [
      Service(
        task = task,
        cluster = 'devcluster',
        role = 'www-data',
        environment = 'prod',
        name = 'hello'
      )
    ]


Jobs without the service bit set only restart up to
`max_task_failures` times and only if they terminated unsuccessfully
either due to human error or machine failure.


### Health Checking

The Executor implements a protocol for rudimentary control of a task via HTTP.  Tasks subscribe for
this protocol by declaring a port named `health`.  Take for example this configuration snippet:

    nginx = Process(
      name = 'nginx',
      cmdline = './run_nginx.sh -port {{thermos.ports[health]}}')

When this Process is included in a job, the job will be allocated a port, and the command line
will be replaced with something like:

    ./run_nginx.sh -port 42816

Where 42816 happens to be the allocated. port.  Typically, the Executor monitors Processes within
a task only by liveness of the forked process.  However, when a `health` port was allocated, it
will also send periodic HTTP health checks.  A task requesting a `health` port must handle the
following requests:

| HTTP request            | Description                             |
| ------------            | -----------                             |
| `GET /health`           | Inquires whether the task is healthy.   |

Please see the
[configuration reference](reference/configuration.md#user-content-healthcheckconfig-objects) for
configuration options for this feature.

#### Snoozing Health Checks

If you need to pause your health check, you can do so by touching a file inside of your sandbox,
named `.healthchecksnooze`

As long as that file is present, health checks will be disabled, enabling users to gather core
dumps or other performance measurements without worrying about Aurora's health check killing
their process.

WARNING: Remember to remove this when you are done, otherwise your instance will have permanently
disabled health checks.
