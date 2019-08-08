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
- `commands`: (required) A list of commands to be run on the network device and parsed. Each entry in the list of `commands` has the following parameters available:
  - `command`: (required) The command to be issued on the network device
  - `set_fact`: (optional) Set the parser output as an Ansible fact for the host in play.
  - `transform`: (optional) A list of tranformations for the parsed data, processed in order. The current transformations can be done:
    - [`camel_to_snake`](/docs/filter/camel_to_snake.md) Convert camelCase keys to snake_case keys.
    - [`expand_vlans`](#expand_vlans) Expand a range of vlans to a list.
    - [`flatten_list_of_dicts`](#flatten_list_of_dicts) Convert a list of dictionaries to a list of values.
    - [`keep_keys`](#keep_keys) Select which keys should be kept in the parsed data.
    - [`nxos_flatten_table_row`](#nxos_flatten_table_row) Remove the nxos TABLE and ROW keys.
    - [`str_to_native`](#str_to_native) Convert string to their native type.
    - [`rekey_on_members`](#rekey_on_members) Turn a list of dictionaries into a dictionary based on a key.
    - [`replace_keys`](#replace_keys) Replace keys in the structured data.
    - [`set_root_key`](#set_root_key) Set a root key for the parsed data.
    - [`stats`](#stats) Generate statistics from the parsed data.
    - [`unnest`](#unnest) Promote a child key to it's parent in the tree.



## Transforms


- <a name="expand_vlans">`expand_vlans`</a>: Expand vlans in range syntax into a list. This is useful when there is a need to `assert` that a vlan in allowed in a trunk later in the playbook.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Ethernet1 switchport
          set_fact: True

    switchports:
      Ethernet1:
        enabled: true
        switchportInfo:
          trunkAllowedVlans: 1-3

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Ethernet1 switchport
          set_fact: True
          transform:
          - name: expand_vlans
            keys:
            - trunkAllowedVlans

    switchports:
      Ethernet1:
        enabled: true
        switchportInfo:
          trunkAllowedVlans:
          - '1'
          - '2'
          - '3'
    ```

- <a name="flatten_list_of_dicts">`flatten_list_of_dicts`</a>: Replaces a list of dictionaries with a list of values. Provide the `key` to match and the `value` to pull from each dictionary.  The `key` is used as a regular expression. This is useful when the engine return lists of dictionaries and only a list of a praticular value within each dictionary is desired.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Eth1/1-2
          set_fact: True

    ansible_facts:
      TABLE_interface:
        ROW_interface:
        - admin_state: down
          encapsulation: ARPA
          eth_autoneg: 'on'
          <...>
          eth_underrun: '0'
          eth_watchdog: '0'
          interface: Ethernet1/1
          medium: broadcast
        - admin_state: up
          encapsulation: ARPA
          eth_autoneg: 'on'
          <...>
          eth_underrun: '0'
          eth_watchdog: '0'
          interface: Ethernet1/2
          medium: broadcast

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Eth1/1-2
          set_fact: True
          transform:
          - name: flatten_list_of_dicts
            flatten:
            - key: ROW_interface
              value: interface

    ansible_facts:
      TABLE_interface:
        ROW_interface:
        - Ethernet1/1
        - Ethernet1/2

    ```

- <a name="keep_keys">`keep_keys`</a>: Provide a list of keys to keep. Comparisons are limited to keys that have a value which is a string, integer, or boolean.  The keys are used as regular expressions. This is useful if the facts need to be limited to only a few specific keys.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Eth1/1-2
          set_fact: True

    ansible_facts:
      TABLE_interface:
        ROW_interface:
        - admin_state: down
          encapsulation: ARPA
          eth_autoneg: 'on'
          <...>
          eth_underrun: '0'
          eth_watchdog: '0'
          interface: Ethernet1/1
          medium: broadcast
        - admin_state: up
          encapsulation: ARPA
          eth_autoneg: 'on'
          <...>
          eth_underrun: '0'
          eth_watchdog: '0'
          interface: Ethernet1/2
          medium: broadcast

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Eth1/1-2
          set_fact: True
          transform:
          - name: keep_keys
            keys:
            - interface
            - admin_state
            - ^state$

    ansible_facts:
       TABLE_interface:
         ROW_interface:
         - admin_state: down
           interface: Ethernet1/1
           state: down
         - admin_state: up
           interface: Ethernet1/2
           state: up

    ```

- <a name="nxos_flatten_table_row">`nxos_flatten_table_row`</a>: Flatten the `TABLE...` and `ROW...` keys when using `native_json` with `nxos`.  The row name is used to generate the new root key. This is useful when using the `native_json` engine with nxos and the `TABLE` and `ROW` keys are not desired in the facts.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show cdp neighbors
          set_fact: True

    ansible_facts:
      TABLE_cdp_neighbor_brief_info:
        ROW_cdp_neighbor_brief_info:
        - capability:
          - router
          - switch
          - Supports-STP-Dispute
          device_id: nxos102(9EFF19FSVFE)
          ifindex: '83886080'
          intf_id: mgmt0
          platform_id: N9K-9000v
          port_id: mgmt0

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show cdp neighbors
          set_fact: True
          transform:
          - name: nxos_flatten_table_row

    ansible_facts:
      cdp_neighbor_brief_info:
       - capability:
         - router
         - switch
         - Supports-STP-Dispute
         device_id: nxos102(9EFF19FSVFE)
         ifindex: '83886080'
         intf_id: mgmt0
         platform_id: N9K-9000v
         port_id: mgmt0

    ```

- <a name="str_to_native">`str_to_native`</a>: Convert values to their native types.  `ast.literal_eval(parsed)` is used for the converstion, in addition, "none", "true", and "false" will be converted to `None`, `True` and `False` respectively.  This is useful when integers, booleans, etc are returned as strings and they should be converted to their respective type.

    ```yaml

    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface counters
          set_fact: True

    ansible_facts:
      TABLE_rx_counters:
        ROW_rx_counters:
        - eth_inpkts: '163243498'
          eth_inucast: '393236'
          interface_rx: mgmt0

    - cli_parse_transform:
        engine: native_json
        commands:
        - command: sho interface counters
          set_fact: True
          transform:
          - name: str_to_native

    ansible_facts:
      TABLE_rx_counters:
        ROW_rx_counters:
        - eth_inpkts: 163246414
          eth_inucast: 393265
          interface_rx: mgmt0

    ```

- <a name="rekey_on_members">`rekey_on_members`</a>:: Convert a list of dictionaries to a dictionary using a specific key. Duplicate keys will result in a list of values for the key. This is useful when the engine returns a list but a dictionary is desired.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface status
          set_fact: True

    ansible_facts:
      TABLE_interface:
        ROW_interface:
        - duplex: full
          interface: mgmt0
          speed: '1000'
          state: connected
          type: --
          vlan: routed
        - duplex: auto
          interface: Ethernet1/1
          speed: auto
          state: disabled
          type: 10g
          vlan: routed

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: sho interface status
          set_fact: True
          transform:
          - name: rekey_on_members
            members:
            - interface

    ansible_facts:
      TABLE_interface:
        ROW_interface:
          Ethernet1/1:
            duplex: auto
            interface: Ethernet1/1
            speed: auto
            state: disabled
            type: 10g
            vlan: routed
          Ethernet1/10:
            duplex: auto
            interface: Ethernet1/10
            speed: auto
            state: notconnect
            type: 10g
            vlan: '1'

    ```


- <a name="replace_keys">`replace_keys`</a>: Change the name of keys in the engine output. The before value is used as a regex. This is useful to modify the output of one command to look like another.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show ip interface
          set_fact: True

    ansible_facts:
       TABLE_intf:
         ROW_intf:
           <...>
           dir-bcast: disabled
           icmp-redirect: disabled
           intf-name: Ethernet1/128
           iod: '132'

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show ip interface
          set_fact: True
          transform:
          - name: replace_keys
            keys:
            - before: intf-name
              after: interface

    ansible_facts:
      TABLE_intf:
        ROW_intf:
          <...>
          dir-bcast: disabled
          icmp-redirect: disabled
          interface: Ethernet1/128
          iod: '132'

    ```


- <a name="set_root_key">`set_root_key`</a>: Set the root key for the parsed data. This is useful for saving facts differently before and after configuration changes for comparison later.

    ```yaml

    # before network configuration change
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface status
          set_fact: True
          transform:
          - name: set_root_key
            key: int_status_before_changes

    ansible_facts:
      int_status_before_changes:
        TABLE_interface:
          ROW_interface:
          - duplex: full
            interface: mgmt0
            speed: '1000'
            state: connected
            type: --
            vlan: routed

    # after network configuration change
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface status
          set_fact: True
          transform:
          - name: set_root_key
            key: int_status_after_changes

    ansible_facts:
      int_status_after_changes:
        TABLE_interface:
          ROW_interface:
          - duplex: full
            interface: mgmt0
            speed: '1000'
            state: connected
            type: --
            vlan: routed
            <...>
      int_status_before_changes:
        TABLE_interface:
          ROW_interface:
          - duplex: full
            interface: mgmt0
            speed: '1000'
            state: connected
            type: --
            vlan: routed

    - assert:
        that: "{{ int_status_before_changes == int_status_after_changes }}"

    ```

- <a name="stats">`stats`</a>: Generate statics for a list of keys.  The parent key name is used for the statistics key name, and each group of statistics is prepended with `count_of`. This is useful to generate summary information from detail engine output. Use the `only_stats` if the original detailed information is not required.

    ```yaml
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface status
          set_fact: True
          transform:
          - name: nxos_flatten_table_row

    ansible_facts:
       interface:
       - duplex: full
         interface: mgmt0
         speed: '1000'
         state: connected
         type: --
         vlan: routed
       - duplex: auto
         interface: Ethernet1/1
         speed: auto
         state: disabled
         type: 10g
         vlan: routed

    - cli_parse_transform:
        engine: native_json
        commands:
        - command: sho interface status
          set_fact: True
          transform:
          - name: nxos_flatten_table_row
          - name: stats
            only_stats: True
            keys:
            - state

    ansible_facts:
      interface_stats:
        count_by_speed:
          '1000': 1
          auto: 130
        count_by_state:
          connected: 2
          disabled: 2
          noOperMembers: 2
          notconnect: 125
        count_by_type:
          --: 3
          10g: 128
        count_by_vlan:
          '1': 128
          routed: 3
        total: 131

    ```

- <a name="unnest">`unnest`</a>: Move a dictionary up one level in the tree. This is useful when the parsed data is unneccesarily complex.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show ip route vrf all
          set_fact: True

    ansible_facts:
      TABLE_vrf:
        ROW_vrf:
          TABLE_addrf:
            ROW_addrf:
              TABLE_prefix:
                ROW_prefix:
                - TABLE_path:
                    ROW_path:
                      clientname: static
                      ipnexthop: 192.168.101.1
                      metric: '0'
                      pref: '1'
                      ubest: 'true'
                      uptime: P1M2DT18H13M43S

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
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

    ansible_facts:
      routes_by_vrf_next_hop:
         management:
           192.168.101.1:
           - 0.0.0.0/0
           192.168.101.14:
           - 192.168.101.0/24
           - 192.168.101.14/32

    ```







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
