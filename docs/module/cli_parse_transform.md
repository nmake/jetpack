# CLI parse and transform

`cli_parse_transform` is an Ansible module that combines the running of commands on a network device with the parsing and transformation of the resulting structured data.

Additionally `cli_parse_transform` can generate statisitics from the parsed data and optionally store the parsed data as Ansible facts.

# Quick start

```
# using the on box | json capabilities
- cli_parse_transform:
    engine: native_json
    commands:
      - command: show interface
        set_fact: True
        transform:
        - name: rekey_on_members
          members:
          - interface

# using pyats
- cli_parse_transform:
    engine: pyats
    commands:
    - command: show version
      set_fact: True
      transform:
      - name: keep_keys
        keys:
        - platform
        - version.*
        - os
```

# Module parameters

- `engine`: (required) Specific the parsing engine to be used, either `native_json`, `native_xml` or `pyats`. For `pyats` the pyats python library needs to be installed on the ansible control node. For `native_xml` the `xmltodict` python library needs to be installed
- `ignore_parser_errors` (optional, bool, default=False) Allow the task to continue when parsing errors are found
- `only_stats` (optional, bool, default=False) Only return summary statisitics for each of the gathered
- `commands`: (required) A list of commands to be run on the network device and parsed. Each entry in the list of `commands` has the following parameters available:
  - `command`: (required) The command to be issued on the network device
  - `set_fact`: (optional) Set the parser output as an Ansible fact for the host in play.
  - `transform`: (optional) A list of tranformations for the parsed data, processed in order. The current transformations can be done:
    - [`camel_to_snake`](/docs/filter/camel_to_snake.md) Convert camelCase keys to snake_case keys.
    - [`expand_vlans`](/docs/filter/expand_vlans.md) Expand a range of vlans to a list.
    - [`flatten_list_of_dicts`](/docs/filter/flatten_list_of_dicts.md) Convert a list of dictionaries to a list of values.
    - [`keep_keys`](/docs/filter/keep_keys.md) Select which keys should be kept in the parsed data.
    - [`nxos_flatten_table_row`](/docs/filter/nxos_flatten_table_row.md) Remove the nxos TABLE and ROW keys.
    - [`rekey_on_members`](/docs/filter/rekey_on_members.md) Turn a list of dictionaries into a dictionary based on a key.
    - [`replace_keys`](/docs/filter/replace_keys.md) Replace keys in the structured data.
    - [`set_root_key`](/docs/filter/set_root_key.md) Set a root key for the parsed data.
    - [`stats`](/docs/filter/stats.md) Generate statistics from the parsed data.
    - [`str_to_native`](/docs/filter/str_to_native.md) Convert string to their native type.
    - [`unnest`](/docs/filter/unnest.md) Promote a child key to it's parent in the tree.

# Examples

See the examples directory for an example of each transform in use.

# Examples showing multiple tranforms in use
```yaml
- hosts: ios101
  gather_facts: false
  roles:
  - network_operating_state
  tasks:
  - cli_parse_transform:
      engine: pyats
      commands:
      - command: show version
        set_fact: True
        transform:
        - name: keep_keys
          keys:
          - platform
          - version.*
          - os
      - command: show interfaces
        set_fact: True
        transform:
        - name: set_root_key
          key: interfaces
        - name: stats
          only_stats: True
          keys:
          - enabled
          - oper_status
      - command: show interfaces
        set_fact: true
        transform:
        - name: keep_keys
          keys:
          - enabled
          - oper_status
        - name: set_root_key
          key: interface_status
      - command: show arp
        set_fact: true
        transform:
        - name: stats
          keys:
          - origin
        - name: set_root_key
          key: arp_neighbors
  - debug:
      var: ansible_facts

- hosts: nxos101
  gather_facts: false
  roles:
  - network_operating_state
  tasks:
  - cli_parse_transform:
      engine: native_json
      commands:
      - command: show interface
        set_fact: True
        transform:
        - name: nxos_flatten_table_row
        - name: stats
          only_stats: True
          keys:
          - admin_state
          - state
      - command: show interface
        set_fact: True
        transform:
        - name: nxos_flatten_table_row
          plural: True
        - name: rekey_on_members
          members:
          - interface
        - name: keep_keys
          keys:
          - .*state.*
          - interface
      - command: show ip interface vrf all
        set_fact: True
        transform:
        - name: nxos_flatten_table_row
          plural: True
        - name: rekey_on_members
          members:
          - intf-name
        - name: keep_keys
          keys:
          - masklen
          - prefix
        - name: replace_keys
          keys:
          - before: ^intfs$
            after: interfaces
        - name: str_to_native
      - command: show interface switchport
        set_fact: True
        transform:
        - name: nxos_flatten_table_row
          plural: True
        - name: keep_keys
          keys:
          - interface
          - oper_mode
          - access_vlan
          - trunk_vlans
        - name: rekey_on_members
          members:
          - interface
        - name: str_to_native
        - name: expand_vlans
          keys:
          - trunk_vlans
      - command: show ip route vrf all
        set_fact: True
        transform:
        - name: nxos_flatten_table_row
          plural: True
        - name: rekey_on_members
          members:
          - vrf-name-out
          - ipnexthop
        - name: keep_keys
          keys:
          - ipprefix
        - name: flatten_list_of_dicts
          flatten:
          - key: .*
            value: ipprefix
        - name: replace_keys
          keys:
          - before: vrfs
            after: routes_by_vrf_next_hop
        - name: unnest
          keys:
          - prefixs
      - command: show ip route vrf all
        set_fact: True
        transform:
        - name: nxos_flatten_table_row
          plural: True
        - name: rekey_on_members
          members:
          - vrf-name-out
        - name: stats
          keys:
          - attached
        - name: keep_keys
          keys:
          - 'true'
          - 'false'
          - total
  - debug:
      var: ansible_facts

- hosts: eos101
  gather_facts: false
  roles:
  - network_operating_state
  tasks:
  - cli_parse_transform:
      engine: native_json
      commands:
        - command: show version
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: keep_keys
            keys:
            - version
            - model_name
          - name: set_root_key
            key: system_info
        - command: show version
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: keep_keys
            keys:
            - mem.*
          - name: set_root_key
            key: memory_stats
        - command: show interface
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: keep_keys
            keys:
            - description
            - hardware
            - interface_status
            - address
            - dhcp
          - name: stats
            keys:
            - interface_status
            - hardware
            - address
        - command: show interface
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: rekey_on_members
            members:
            - interface_status
          - name: keep_keys
            keys:
            - name
          - name: flatten_list_of_dicts
            flatten:
            - key: .*
              value: name
          - name: replace_keys
            keys:
            - before: ^(interfaces)$
              after: \1_by_status
        - command: show interface switchport
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: keep_keys
            keys:
            - enabled
            - mode
          - name: unnest
            keys:
            - switchport_info
        - command: show lldp neighbors
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: rekey_on_members
            members:
            - port
          - name: keep_keys
            keys:
            - neighbor_device
          - name: flatten_list_of_dicts
            flatten:
            - key: .*
              value: neighbor_device
          - name: set_root_key
            key: lldp_neighbors_by_local_port
          - name: unnest
            keys:
            - lldp_neighbors
        - command: show lldp neighbors
          set_fact: True
          transform:
          - name: camel_to_snake
          - name: stats
            only_stats: True
            keys:
            - port
            - neighbor_device
  - debug:
      var: ansible_facts

```
