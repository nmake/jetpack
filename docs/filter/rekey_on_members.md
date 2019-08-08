## `rekey_on_members`

Convert a list of dictionaries to a dictionary using a specific key. Duplicate keys will result in a list of values for the key. This is useful when the engine returns a list but a dictionary is desired.

### Used with cli_parse_transform as a transform

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

- debug:
    msg: "{{ data|nmake.jetpack.rekey_on_members(['interface']) }}"

# result
msg:
  ROW_interface:
    Ethernet1/1:
      duplex: full
      interface: Ethernet1/1
      speed: auto
      state: connected
      type: 10g
      vlan: '1'
    Ethernet1/2:
      duplex: full
      interface: Ethernet1/2
      speed: auto
      state: connected
      type: 10g
      vlan: '1'
  TABLE_interface: null

```
