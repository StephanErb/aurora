### Process Logs

#### Log destination
By default, Thermos will write process stdout/stderr to log files in the sandbox. Process object configuration
allows specifying alternate log file destinations like streamed stdout/stderr or suppression of all log output.
Default behavior can be configured for the entire cluster with the following flag (through the `-thermos_executor_flags`
argument to the Aurora scheduler):

    --runner-logger-destination=both

`both` configuration will send logs to files and stream to parent stdout/stderr outputs.

See [this document](configuration-reference.md#logger) for all destination options.

#### Log rotation
By default, Thermos will not rotate the stdout/stderr logs from child processes and they will grow
without bound. An individual user may change this behavior via configuration on the Process object,
but it may also be desirable to change the default configuration for the entire cluster.
In order to enable rotation by default, the following flags can be applied to Thermos (through the
-thermos_executor_flags argument to the Aurora scheduler):

    --runner-logger-mode=rotate
    --runner-rotate-log-size-mb=100
    --runner-rotate-log-backups=10

In the above example, each instance of the Thermos runner will rotate stderr/stdout logs once they
reach 100 MiB in size and keep a maximum of 10 backups. If a user has provided a custom setting for
their process, it will override these default settings.
