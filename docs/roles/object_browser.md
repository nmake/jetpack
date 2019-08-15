![screenshot](https://github.com/nmake/jetpack/raw/master/docs/roles/object_broswer/object_broswer_screenshot.png)

# Object browser

`object_browser` is an Ansible role that generates an HTML file from a hosts facts.

The HTML file is in navigatable tree format and provides and easy way to review and report on both inventory information for a host or information gathered about a host during the playbook run.

Reports can be generated in per host format or all-in-one, the later includes all host in a sigle HTML file.

**Note:**

Since the resulting reports may contain sensitive information, please take the ncessary security precautions.

## Quick start

Render all the hostvars for all hosts in a reports directory within the playbook directory, one file per host.

```yaml
- hosts: all
  gather_facts: false
  tasks:
  - include_role:
      role: nmake.jetpack.object_browser
```

Render all the hostvars for all hosts in a reports directory within the playbook directory, in a single file.

```yaml
- hosts: all
  gather_facts: false
  tasks:
  - include_role:
      role: nmake.jetpack.object_browser
    vars:
      report_format: all_in_one
```

## Role parameters

The following parameters can be used to customize the report output:

- `title` (optional, string) The title for the report
- `summary` (optional, string) The summary information for the report
- `filename` (optional, string) The filename for the report
- `directory` (optional, string) The directory in which the reports will be placed
- `dotted_key_paths` (optional, list) A list of keypaths withing the hostvars to include in the report
- `report_format` (optional, string, default=`per_host`) The report format, either `per_host` or `all_in_one`


## Examples

### Limit the data in the report

A list of keys to include can per provided.  Each key is in dot-delimited format and will be collected from the hostvars.

For instance, to report only on a hosts `ansible_inventory_sources`, `groups` and full ansible version:

```yaml
- hosts: all
  gather_facts: false
  tasks:
  - include_role:
      role: nmake.jetpack.object_browser
    vars:
      dotted_key_paths:
      - ansible_inventory_sources
      - ansible_version.full
      - groups
```

### Set the report metadata

```yaml
hosts: all
 gather_facts: false
 tasks:
 - include_role:
     role: nmake.jetpack.object_browser
   vars:
     directory: ./my_reports
     filename: "all_hostvars.html"
     title: "Hostvars for all hosts"
     summary: "All hostvars for all hosts"
     report_format: all_in_one
```

### Used with the network_change_log callback plugin, create a change log

```yaml
- hosts: all
  gather_facts: false
  tasks:
  - nxos_config:
      lines:
      - description "management interface {{ 100 | random }}"
      parents: interface mgmt0
  - include_role:
      role: nmake.jetpack.object_browser
    vars:
      dotted_key_paths:
      - network_change_log.commands
      - network_change_log.summary
      directory: ./reports
      filename: "change_log.html"
      title: "Change log for all hosts"
      summary: "Change made to device using Ansible playbook"
      report_format: all_in_one
```

### Used with the gather_states role to collect parsed `show` command output

```yaml
- hosts: nxos101
  gather_facts: false
  vars:
    state_per_os:
      nxos:
        gather_states:
        - all
        - '!fex'
        - '!vlan.private_vlan'
        - '!vpc'
  roles:
  - role: nmake.jetpack.gather_states
    gather_states: "{{ state_per_os[ansible_network_os]['gather_states'] }}"
  - role: nmake.jetpack.object_browser
    dotted_key_paths:
    - gathered_states
    filename: "{{ inventory_hostname }}_gathered_states.html"

- hosts: nxos101
  gather_facts: false
  roles:
  - role: nmake.jetpack.gather_states
    only_stats: True
    fact_key: stats_info
    gather_states:
    - all
    - '!vpc'
  - role: nmake.jetpack.object_browser
    dotted_key_paths:
    - stats_info
    filename: "{{ inventory_hostname }}_gathered_states_stats_only.html"
```
