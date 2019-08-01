
[![asciicast](https://asciinema.org/a/l21jJTCCjoaCJH3keGqJhdZvW.png)](https://asciinema.org/a/l21jJTCCjoaCJH3keGqJhdZvW?speed=0.5&autoplay=1)

# Network Change Log

## Overview

Network change log is an Ansible callback plugin for network engineers and network operators.  It provides customized output from an Ansible playbook that brings network device changes front and center.

```
TASK [Change the description of an interface] *************
changed: [eos101]
eos101:
- task: Change the description of an interface and show the command output by using the 'ncl' magic tag
  commands:
  - interface Ethernet2
  - description 1559843014
```

Following a playbook run, all device changes are summarized and provided to the user

```
NETWORK CHANGE LOG ****************************************
eos101:
- task: Change the description of an interface
  commands:
  - interface Ethernet2
  - description 1559843014
- task: Save the configuration if anything has changed
  commands:
  - copy run start
```

## Quick start

### Download from ansible galaxy


1) Download the role from ansible_galaxy into your roles directory
```
ansible-galaxy install -p roles cidrblock.network_change_log
```
2) Enable the callback plugin in your `ansible.cfg`
```
[defaults]
callback_whitelist = network_change_log
```
3) Initialize the role by loading it at the top of your playbook

```
- hosts: localhost
  gather_facts: False
  roles:
  - cidrblock.network_change_log
```
4) Run your playbook


### Using the role
1) Download this repository into your playbook's role directory
2) Enable the callback plugin in your `ansible.cfg`
```
[defaults]
callback_whitelist = network_change_log
```
3) Initialize the role by loading it at the top of your playbook

```
- hosts: localhost
  gather_facts: False
  roles:
  - network_change_log
```
4) Run your playbook

### Using the default callback directory
1) Download this repository and copy the the `network_callback_plugin/callback_plugins/network_change_log.py` to `~/.ansible/plugins/callback`
```
$ cp network_change_log/callback_plugins/network_change_log.py ~/.ansible/plugins/callback
```
2) Enable the callback plugin in your `ansible.cfg`
```
[defaults]
callback_whitelist = network_change_log
```
3) Run your playbook

## Configuration

The behaviour of the network change log callback plugin and be modified by adding a `network_change_log` section to the ansible.cfg.  The following configuration parameters are supported:

```
changed_only:
  description: Only include tasks that are changed
  default: True
detailed_result:
  description: Include the detailed result for each task
  default: False
logging:
   description: Show the commands issued for every task
   default: False
module_name_regex:
  description: Only log tasks using the following modules
  default: '^(eos|nxos|ios|junos|vyos|cli)'
network_cli_only:
  description: Only log for hosts where ansible_connection=network_cli
  default: True
summary_log:
  description: After the play recap, show the full change log for all hosts
  default: True
timestamps:
  description: Include the start, end and duration for each task in the output
  default: False
```

See the `ansible.cfg` file in the `examples` directory for an example.

## Magic tags

The bahaviour of the network change log callback plugin can be modified during a playbook run by assigning `tags` to a task.

The currently supported magic tags include:

`ncl`: When a task has this tag, the commands issued to the network device will be immediately shown when the task completes.

`ncl_last`: The last entry in the network change log for a device will be shown after any task that has this tag

`ncl_full`: All entries in the change log for a network device will be shown following any task with the nc_full tag

`ncl_logging_enable`: Enable command logging for all remaining tasks.  This is has the same effect as adding the `ncl` tag to all tasks or setting the `ansible.cfg` `[network_change_log]` `logging` value to `true`

`ncl_logging_disable`: Disable command logging for all remaining tasks.

## host_vars

Network change log records information in each host's `host_vars`.  To see what network change log has tracked during a playbook run add a `debug` task to your playbook.

```
- debug:
    var: hostvars[inventory_hostname]['network_change_log']
```

The hostvars can be used to determine if a device has changed within a playbook or to save a change log to a file.

The new `summary` key tracks all tasks in the playbook and the `tasks` key contains only tasks based on the configuration in the `ansible.cfg` file.

Try tracking everything that happens within a playbook with verbose screen output by modifying your `ansible.cfg` and save the change log to a file:

```
[network_change_log]
changed_only = false
detailed_result = true
logging = true
module_name_regex = '.*'
network_cli_only = false
summary_log = true
timestamps = true


- name: Save the network change log for each host to a file
  copy:
    content: "{{ network_change_log|to_nice_yaml }}"
    dest: "ncl_{{ inventory_hostname }}.yaml"
  when: network_change_log is defined

```

See the `site.yml` file in the examples directory for an example of the new hostvars in use within a playbook.

### Sample hostvars
```
ok: [vyos101] => {
    "hostvars[inventory_hostname]['network_change_log']": {
        "summary": {
            "changed": 2,
            "failed": 0,
            "ok": 3,
            "skipped": 0,
            "total": 3,
            "unreachable": 0
        },
        "tasks": [
            {
                "action": "vyos_config",
                "args": {
                    "lines": [
                        "set interfaces ethernet eth2 description {{ timestamp }}"
                    ]
                },
                "changed": true,
                "commands": [
                    "set interfaces ethernet eth2 description 1559848441"
                ],
                "duration": "0:00:03.407107",
                "end": "2019-06-06 12:14:13.758308",
                "failed": false,
                "loop": null,
                "name": "Change the description of an interface",
                "ok": true,
                "skipped": false,
                "start": "2019-06-06 12:14:10.351201",
                "unreachable": false
            },
            {
                "action": "cli_command",
                "args": {
                    "command": "{{ save_command[ansible_network_os] }}"
                },
                "changed": true,
                "commands": [
                    "write"
                ],
                "duration": "0:00:00.954392",
                "end": "2019-06-06 12:14:17.619433",
                "failed": false,
                "loop": null,
                "name": "Save the configuration if anything has changed",
                "ok": true,
                "skipped": false,
                "start": "2019-06-06 12:14:16.665041",
                "unreachable": false
            }
        ],
        "time": {
            "elapsed": "0:00:17.823904",
            "start": "2019-06-06 12:13:59.795529"
        }
    }
}
```
