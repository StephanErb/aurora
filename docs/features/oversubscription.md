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
