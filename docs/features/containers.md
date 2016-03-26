
TODO

(copy & paste dump below)


### Considerations for running jobs in docker containers
In order for Aurora to launch jobs using docker containers, a few extra configuration options
must be set.  The [docker containerizer](http://mesos.apache.org/documentation/latest/docker-containerizer/)
must be enabled on the mesos slaves by launching them with the `--containerizers=docker,mesos` option.

By default, Aurora will configure Mesos to copy the file specified in `-thermos_executor_path`
into the container's sandbox.  If using a wrapper script to launch the thermos executor,
specify the path to the wrapper in that argument. In addition, the path to the executor pex itself
must be included in the `-thermos_executor_resources` option. Doing so will ensure that both the
wrapper script and executor are correctly copied into the sandbox. Finally, ensure the wrapper
script does not access resources outside of the sandbox, as when the script is run from within a
docker container those resources will not exist.

In order to correctly execute processes inside a job, the docker container must have python 2.7
installed.

A scheduler flag, `-global_container_mounts` allows mounting paths from the host (i.e., the slave)
into all containers on that host. The format is a comma separated list of host_path:container_path[:mode]
tuples. For example `-global_container_mounts=/opt/secret_keys_dir:/mnt/secret_keys_dir:ro` mounts
`/opt/secret_keys_dir` from the slaves into all launched containers. Valid modes are `ro` and `rw`.

If you would like to supply your own parameters to `docker run` when launching jobs in docker
containers, you may use the following flags:

    -allow_docker_parameters
    -default_docker_parameters

`-allow_docker_parameters` controls whether or not users may pass their own configuration parameters
through the job configuration files. If set to `false` (the default), the scheduler will reject
jobs with custom parameters. *NOTE*: this setting should be used with caution as it allows any job
owner to specify any parameters they wish, including those that may introduce security concerns
(`privileged=true`, for example).

`-default_docker_parameters` allows a cluster operator to specify a universal set of parameters that
should be used for every container that does not have parameters explicitly configured at the job
level. The argument accepts a multimap format:

    -default_docker_parameters="read-only=true,tmpfs=/tmp,tmpfs=/run"
