## `stats`

Generate statics for a list of keys.  The parent key name is used for the statistics key name, and each group of statistics is prepended with `count_of`. This is useful to generate summary information from detailed output. Use the `only_stats` if the original detailed information is not required.

### Used with cli_parse_transform as a transform

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
  stats:
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

### Used a jinja filter

```yaml
- set_fact:
    data:
      TABLE_interface:
      ROW_interface:
      - interface: Ethernet1/1
        state: connected
        vlan: '1'
        duplex: full
        speed: auto
        type: 10g
      - interface: Ethernet1/2
        state: connected
        vlan: '1'
        duplex: full
        speed: auto
        type: 10g
      - interface: Ethernet1/3
        state: notconnect
        vlan: '1'
        duplex: auto
        speed: auto
        type: 10g

- name: Generate interface stats, and only return stats
  debug:
    msg: "{{ data|nmake.jetpack.stats(['state', 'type'], True) }}"

# result
msg:
  ROW_interface_stats:
    count_by_state:
      connected: 2
      notconnect: 1
    count_by_type:
      10g: 3
    total: 3
```
