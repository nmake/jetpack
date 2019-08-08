## `set_root_key`

Set the root key for the data. This is useful for saving facts differently before and after configuration changes for comparison later.

### Used with cli_parse_transform as a transform

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

### Used a jinja filter

```yaml
- set_fact:
    data:
      header_str: |-
        Cisco Nexus Operating System (NX-OS) Software
        TAC support: http://www.cisco.com/tac
        Nexus 9000v is a demo version of the Nexus Operating System
      bios_ver_str:
      kickstart_ver_str: 9.2(2)
      bios_cmpl_time:
      manufacturer: Cisco Systems, Inc.

- name: Set the root key
  debug:
    msg: "{{ data|nmake.jetpack.set_root_key('show_version') }}"

# result
msg:
  show_version:
    bios_cmpl_time: null
    bios_ver_str: null
    header_str: |-
      Cisco Nexus Operating System (NX-OS) Software
      TAC support: http://www.cisco.com/tac
      Nexus 9000v is a demo version of the Nexus Operating System
    kickstart_ver_str: 9.2(2)
    manufacturer: Cisco Systems, Inc.

```
