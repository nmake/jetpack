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

```
