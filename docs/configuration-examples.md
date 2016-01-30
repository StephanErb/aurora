

Basic Examples
==============

These are provided to give a basic understanding of simple Aurora jobs.

### hello_world.aurora

Put the following in a file named `hello_world.aurora`, substituting your own values
for values such as `cluster`s.

    import os
    hello_world_process = Process(name = 'hello_world', cmdline = 'echo hello world')

    hello_world_task = Task(
      resources = Resources(cpu = 0.1, ram = 16 * MB, disk = 16 * MB),
      processes = [hello_world_process])

    hello_world_job = Job(
      cluster = 'cluster1',
      role = os.getenv('USER'),
      task = hello_world_task)

    jobs = [hello_world_job]

Then issue the following commands to create and kill the job, using your own values for the job key.

    aurora job create cluster1/$USER/test/hello_world hello_world.aurora

    aurora job kill cluster1/$USER/test/hello_world

### Environment Tailoring

#### hello_world_productionized.aurora

Put the following in a file named `hello_world_productionized.aurora`, substituting your own values
for values such as `cluster`s.

    include('hello_world.aurora')

    production_resources = Resources(cpu = 1.0, ram = 512 * MB, disk = 2 * GB)
    staging_resources = Resources(cpu = 0.1, ram = 32 * MB, disk = 512 * MB)
    hello_world_template = hello_world(
        name = "hello_world-{{cluster}}"
        task = hello_world(resources=production_resources))

    jobs = [
      # production jobs
      hello_world_template(cluster = 'cluster1', instances = 25),
      hello_world_template(cluster = 'cluster2', instances = 15),

      # staging jobs
      hello_world_template(
        cluster = 'local',
        instances = 1,
        task = hello_world(resources=staging_resources)),
    ]

Then issue the following commands to create and kill the job, using your own values for the job key

    aurora job create cluster1/$USER/test/hello_world-cluster1 hello_world_productionized.aurora

    aurora job kill cluster1/$USER/test/hello_world-cluster1
