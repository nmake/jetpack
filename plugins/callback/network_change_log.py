# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from datetime import datetime
import re
from ansible.plugins.callback import CallbackBase
from ansible.module_utils.six import iteritems
from ansible.utils.color import hostcolor, stringc
from ansible import constants as C

DOCUMENTATION = '''
callback: network_change_log
type: aggregate
short_description:
description:
-
version_added: '1.0'
author:
- Brad Thornton
requirements:
- whitelisting in configuration
options:
  changed_only:
    description: Only include tasks that are changed
    ini:
        - section: network_change_log
          key: changed_only
          version_added: '1.0'
    default: True
    type: bool
  detailed_result:
    description: Include the detailed result for each task
    ini:
        - section: network_change_log
          key: detailed_result
          version_added: '1.0'
    default: False
    type: bool
  logging:
     description: Show the commands issued for every task
     ini:
         - section: network_change_log
           key: logging
           version_added: '1.0'
     default: False
     type: bool
  module_name_regex:
    description: Only log tasks using the following modules
    ini:
        - section: network_change_log
          key: module_name_regex
          version_added: '1.0'
    default: '^(eos|nxos|ios|junos|vyos|cli)'
    type: str
  network_cli_only:
    description: Only log for hosts where ansible_connection=network_cli
    ini:
        - section: network_change_log
          key: network_cli_only
          version_added: '1.0'
    default: True
    type: bool
  summary_log:
    description: After the play recap, show the full change log for all hosts
    ini:
        - section: network_change_log
          key: summary_log
          version_added: '1.0'
    default: True
    type: bool
  timestamps:
    description: Include the start, end and duration for each task in the output
    ini:
        - section: network_change_log
          key: timestamps
          version_added: '1.0'
    default: False
    type: bool
'''

# pylint: disable=W0212

class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 1.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'change_log'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._vm = None
        self._task_cache = {}
        self._last_task_start = None
        self._start_time = None
        self._changed_only = None
        self._detailed_result = None
        self._logging = None
        self._module_name_regex = None
        self._network_cli_only = None
        self._summary_log = None
        self._timestamps = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)
        self._detailed_result = self.get_option('detailed_result')
        self._changed_only = self.get_option('changed_only')
        self._logging = self.get_option('logging')
        self._module_name_regex = self.get_option('module_name_regex')
        self._network_cli_only = self.get_option('network_cli_only')
        self._summary_log = self.get_option('summary_log')
        self._timestamps = self.get_option('timestamps')

    def _update_change_log(self, result, stat):
        host = result._host
        host_vars = self._vm.get_vars(host=host)
        if ((self._network_cli_only and
             re.match(self._module_name_regex, result._task.action) and
             host_vars['ansible_connection'] == "network_cli") or
                not self._network_cli_only):
            clog = host_vars['network_change_log']
            clog['summary']['total'] += 1
            if result.is_changed():
                clog['summary']['changed'] += 1
            clog['summary'][stat] += 1
            tstamp = datetime.now()
            clog['time']['elapsed'] = str(tstamp - self._start_time)

            if ((self._changed_only and result._result['changed']) or
                    not self._changed_only):
                this_task = self._task_cache[(result._task._uuid, host.name)]
                task_start_time = datetime.strptime(this_task['start'],
                                                    "%Y-%m-%d %H:%M:%S.%f")

                this_task['changed'] = result._result.get('changed')
                this_task['failed'] = (stat == 'failed')
                this_task['ok'] = (stat == 'ok')
                this_task['skipped'] = (stat == 'skipped')
                this_task['unreachable'] = (stat == 'unreachable')
                this_task['end'] = str(tstamp)
                this_task['duration'] = str(tstamp - task_start_time)
                if self._detailed_result:
                    this_task['result'] = result._result
                # get the commands from the invocation in not in the result
                # this should cover the _command modules and cli_
                if 'commands' in result._result:
                    commands = result._result['commands']
                elif 'commands' in result._task.args:
                    commands = result._task.args['commands']
                elif 'command' in result._task.args:
                    commands = [result._task.args['command']]
                else:
                    commands = []
                this_task['commands'] = commands
                clog['tasks'].append(this_task)
                clog['commands'].extend(commands)

            self._vm.set_host_facts(host.name, {"network_change_log": clog})
            del self._task_cache[(result._task._uuid, host.name)]
            if 'ncl' in result._task.tags or self._logging:
                self._print_host_change_log(host, True)
        if 'ncl_full' in result._task.tags:
            self._print_host_change_log(host, False)
        if 'ncl_last' in result._task.tags:
            self._print_host_change_log(host, True)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._update_change_log(result, 'failed')

    def v2_runner_on_ok(self, result):
        self._update_change_log(result, 'ok')

    def v2_runner_on_skipped(self, result):
        self._update_change_log(result, 'skipped')

    def v2_runner_on_unreachable(self, result):
        self._update_change_log(result, 'unreachable')

    def v2_runner_on_start(self, host, task):
        if 'ncl_logging_enable' in task.tags:
            self._logging = True
        if 'ncl_logging_disable' in task.tags:
            self._logging = False
        host_vars = self._vm.get_vars(host=host)
        if ((self._network_cli_only and
             re.match(self._module_name_regex, task.action) and
             host_vars['ansible_connection'] == "network_cli") or
                not self._network_cli_only):
            if 'network_change_log' not in host_vars:
                tstamp = str(self._start_time)
                clog = {
                    "time": {
                        "start": tstamp,
                        "elapsed": None,
                    },
                    "summary": {
                        "total": 0,
                        "ok": 0,
                        "failed": 0,
                        "changed": 0,
                        "skipped": 0,
                        "unreachable": 0},
                    "tasks": [],
                    "commands": []}
                self._vm.set_host_facts(host.name, {"network_change_log": clog})
            new_task = {"name": task.get_name().strip(),
                        "action": task.action,
                        "loop": task.loop,
                        "start": str(datetime.now()),
                        "args": task.args}
            self._task_cache[(task._uuid, host.name)] = new_task

    def v2_playbook_on_play_start(self, play):
        self._vm = play.get_variable_manager()

    def v2_playbook_on_start(self, playbook):
        self._start_time = datetime.now()

    def v2_playbook_on_stats(self, stats):
        self._print_full_change_log(stats)

    def _print_full_change_log(self, stats):
        if self._summary_log:
            self._display.banner("NETWORK CHANGE LOG")
            for host, hvars in iteritems(self._vm.get_vars()['hostvars']):
                hstat = stats.summarize(host)
                if 'network_change_log' in hvars:
                    self._display.display(hostcolor("%s:" % host, hstat))
                    for task in hvars['network_change_log']['tasks']:
                        self._print_task(task)
            self._display.display(' ')

    def _print_host_change_log(self, host, last=False):
        host_vars = self._vm.get_vars(host=host)
        if 'network_change_log' in host_vars:
            if last:
                tasks = host_vars['network_change_log']['tasks'][-1:]
            else:
                tasks = host_vars['network_change_log']['tasks']
            if tasks:
                if last:
                    color = color_from_task(tasks[0])
                else:
                    color = C.COLOR_OK  # pylint: disable=E1101
                hoststr = "%s:" % stringc(host_vars['inventory_hostname'],
                                          color)
                self._display.display(hoststr)
                for task in tasks:
                    self._print_task(task)
                self._display.display(' ')

    def _print_task(self, task):
        color = color_from_task(task)
        taskstr = "- task: %s" % (task['name'])
        self._display.display(stringc(taskstr, color))
        if task['commands']:
            cmdstr = "commands:"
            self._display.display(stringc(" "*2 + cmdstr, color))
            for command in task['commands']:
                cmdstr = " "*2 + "- %s" % stringc(command, color)
                self._display.display(cmdstr)
        else:
            cmdstr = " "*2 + "%s" % stringc("commands: []", color)
            self._display.display(cmdstr)
        if self._timestamps:
            for timestamp in ['start', 'end', 'duration']:
                tstr = " "*2 + "%s" % stringc("%s: %s" % (timestamp,
                                                          task[timestamp]),
                                              color)
                self._display.display(tstr)

def color_from_task(task):
    if task['changed']:
        color = C.COLOR_CHANGED  # pylint: disable=E1101
    elif task['ok']:
        color = C.COLOR_OK       # pylint: disable=E1101
    elif task['failed']:
        color = C.COLOR_ERROR    # pylint: disable=E1101
    elif task['skipped']:
        color = C.COLOR_SKIPPED  # pylint: disable=E1101
    return color
