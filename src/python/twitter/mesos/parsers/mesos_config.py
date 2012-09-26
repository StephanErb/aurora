import os

from twitter.common.lang import Compatibility

from .base import EntityParser
from .proxy_config import ProxyConfig
from .mesos_thrift import convert as convert_mesos_to_thrift


class MesosConfig(ProxyConfig):
  UPDATE_CONFIG_DEFAULTS = {
    'batchSize':           1,
    'restartThreshold':   30,
    'watchSecs':          30,
    'maxPerShardFailures': 0,
    'maxTotalFailures':    0,
  }

  @staticmethod
  def execute(config_file):
    """
      Execute the .mesos configuration "config_file" in the context of preloaded
      library functions, e.g. mesos_include.
    """
    env = {}
    deposit_stack = [os.path.dirname(config_file)]
    def ast_executor(filename):
      actual_file = os.path.join(deposit_stack[-1], filename)
      deposit_stack.append(os.path.dirname(actual_file))
      execfile(actual_file, env)
      deposit_stack.pop()
    env.update({'mesos_include': lambda filename: ast_executor(filename) })
    execfile(config_file, env)
    return env

  @staticmethod
  def get_update_config(job_dict, snaked=False):
    """Expand the update_config in either snake or camelcase format."""
    def snake(st):
      return ''.join((ch if ch.islower() else '_%s' % ch.lower()) for ch in st)
    config = job_dict.get(snake('updateConfig'), job_dict.get('updateConfig', {}))
    filled = {}
    for key in MesosConfig.UPDATE_CONFIG_DEFAULTS:
      store_key = snake(key) if snaked else key
      if key in config:
        filled[store_key] = config[key]
      elif snake(key) in config:
        filled[store_key] = config[snake(key)]
      else:
        filled[store_key] = MesosConfig.UPDATE_CONFIG_DEFAULTS[key]
    return filled

  @staticmethod
  def assert_in(dic, key, with_types, errors):
    def type_repr(tps):
      return ' '.join(typ.__name__ for typ in tps)
    if key not in dic:
      errors.append('Missing key %s in task dictionary' % key)
    elif with_types and not isinstance(dic[key], with_types):
      errors.append('Value for key %s must be of type(s): %s, got %s' % (
          key, type_repr(with_types), dic[key]))

  @staticmethod
  def fill_task_defaults(task_dict, errors):
    if not isinstance(task_dict, dict):
      errors.append('Task must be a dictionary!')
      return

    task_dict = task_dict.copy()

    # optionals
    task_dict['daemon'] = bool(task_dict.get('daemon', False))
    task_dict['priority'] = int(task_dict.get('priority', 0))
    task_dict['max_task_failures'] = int(task_dict.get('max_task_failures', 1))
    task_dict['production'] = bool(task_dict.get('production', False))

    # deprecated
    if 'max_per_host' in task_dict:
      print('WARNING: task.max_per_host is deprecated')
    if 'avoid_jobs' in task_dict:
      print('WARNING: task.avoid_jobs is deprecated')

    if 'package' in task_dict:
      errors.append('"package" must be specified at the job level, not the task level')

    if 'constraints' in task_dict:
      errors.append('"constraints" must be specified at the job level, not the task level')

    # requires
    MesosConfig.assert_in(task_dict, 'num_cpus', Compatibility.numeric, errors)
    MesosConfig.assert_in(task_dict, 'ram_mb', Compatibility.integer, errors)
    MesosConfig.assert_in(task_dict, 'disk_mb', Compatibility.integer, errors)
    MesosConfig.assert_in(task_dict, 'start_command', Compatibility.string, errors)
    if 'num_cpus' in task_dict:
      task_dict['num_cpus'] = float(task_dict['num_cpus'])
    return task_dict

  @staticmethod
  def validate_task_resources(task_dict, errors):
    # requires
    resources = ('num_cpus', 'ram_mb', 'disk_mb')
    if any(task_dict.get(resource, 0) <= 0 for resource in resources):
      errors.append('Resources must be positive!  Got %s' % (
          ' '.join('%s:%r' % (resource, task_dict.get(resource)) for resource in resources)))

  @staticmethod
  def fill_defaults(config):
    """Validates a configuration object.
    This will make sure that the configuration object has the appropriate
    'magic' fields defined, and are of the correct types.

    We require a job name, and a task definition dictionary
    (which is uninterpreted).  A number of instances may also be specified,
    but will default to 1.

    Returns the job configurations found in the configuration object.
    """

    if 'jobs' not in config or not isinstance(config['jobs'], list):
      raise MesosConfig.InvalidConfig(
        'Configuration must define a python list named "jobs"')

    jobs = {}

    for job in config['jobs']:
      errors = []
      if 'name' not in job:
        errors.append('Missing required option: name')
      elif job['name'] in jobs:
        errors.append('Duplicate job definition')
      if 'owner' in job:
        errors.append("'owner' is deprecated.  Please use role.")
        if 'role' in job:
          errors.append('Ambiguous specification: both owner and role specified.')
        else:
          job['role'] = job['owner']
          del job['owner']
      else:
        if 'role' not in job:
          errors.append('Must specify role.')

      if 'cluster' not in job:
        errors.append('Missing required option: cluster')

      if 'task' not in job:
        errors.append('Missing required option: task')
      else:
        job['task'] = MesosConfig.fill_task_defaults(job['task'], errors)
        MesosConfig.validate_task_resources(job['task'], errors)

      if 'package' in job:
        if not isinstance(job['package'], (list, tuple)) or len(job['package']) != 3:
          errors.append('Job package must be a tuple of (name, role, version), got: %r' %
              job['package'])

      if errors:
        raise MesosConfig.InvalidConfig('Invalid configuration: %s\n' % '\n'.join(errors))

      # Default to a single instance.
      job['instances'] = int(job.get('instances', 1))
      job['cron_schedule'] = job.get('cron_schedule', '')
      job['cron_collision_policy'] = job.get('cron_collision_policy', 'KILL_EXISTING')
      job['update_config'] = MesosConfig.get_update_config(job)
      jobs[job['name']] = job
    return jobs

  def __init__(self, filename, name=None):
    """Loads a job configuration from a file and validates it.

    Returns a validated configuration object.
    """
    env = MesosConfig.execute(filename)
    self._config = MesosConfig.fill_defaults(env)
    if name is None:
      if len(self._config) == 1:
        self._config = self._config.values()[0]
      else:
        raise ValueError('Must specify job name in multi-job configuration!')
    else:
      if name not in self._config:
        raise ValueError('Unknown job %s! Perhaps you meant one of these?:\n  %s' % (
          name, '\n  '.join(self._config.keys())
        ))
      self._config = self._config[name]
    self._name = self._config['name']

  def job(self):
    return convert_mesos_to_thrift(self._config)

  def ports(self):
    return EntityParser.match_ports(self._config['task']['start_command'])

  def hdfs_path(self):
    return self._config['task'].get('hdfs_path')

  def set_hdfs_path(self, path):
    self._config['task']['hdfs_path'] = path

  def role(self):
    return self._config['role']

  def cluster(self):
    return self._config.get('cluster')

  def name(self):
    return self._name

  def update_config(self):
    return self._config['update_config']

  def package(self):
    """Return a 3-tuple of (role, name, version)"""
    return self._config.get('package')
