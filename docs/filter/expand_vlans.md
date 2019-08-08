
## `expand_vlans`

Expand vlans in range syntax into a list. This is useful when there is a need to `assert` that a vlan in allowed in a trunk later in the playbook.

### Used with cli_parse_transform as a transform

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

### Used a jinja filter

```yaml

- set_fact:
    data:
      TABLE_interface:
      ROW_interface:
        interface: Ethernet1/1
        switchport: Enabled
        oper_mode: access
        access_vlan: '1'
        access_vlan_name: default
        native_vlan: '1'
        trunk_vlans: 1-5
        voice_vlan_name: none

- debug:
    msg: "{{ data|nmake.jetpack.expand_vlans(['trunk_vlans']) }}"

# result
msg:
  ROW_interface:
    access_vlan: '1'
    access_vlan_name: default
    interface: Ethernet1/1
    native_vlan: '1'
    oper_mode: access
    switchport: Enabled
    trunk_vlans:
    - '1'
    - '2'
    - '3'
    - '4'
    - '5'
    voice_vlan_name: none
  TABLE_interface: null

```
