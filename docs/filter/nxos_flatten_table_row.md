## `nxos_flatten_table_row`

Flatten the `TABLE...` and `ROW...` keys when using json data from an nxos device.  The row name is used to generate the new root key. 

### Used with cli_parse_transform as a transform

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

- name: Remove the TABLE and ROW, set the ROW to plural
  debug:
    msg: "{{ data|nmake.jetpack.nxos_flatten_table_row(True) }}"

# result
msg:
  interfaces:
  - duplex: full
    interface: Ethernet1/1
    speed: auto
    state: connected
    type: 10g
    vlan: '1'
  - duplex: full
    interface: Ethernet1/2
    speed: auto
    state: connected
    type: 10g
    vlan: '1'

```
