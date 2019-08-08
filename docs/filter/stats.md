## `stats`

Generate statics for a list of keys.  The parent key name is used for the statistics key name, and each group of statistics is prepended with `count_of`. This is useful to generate summary information from detail engine output. Use the `only_stats` if the original detailed information is not required.

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
