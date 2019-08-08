## `flatten_list_of_dicts`

Replaces a list of dictionaries with a list of values. Provide the `key` to match and the `value` to pull from each dictionary.  The `key` is used as a regular expression. This is useful when the engine return lists of dictionaries and only a list of a praticular value within each dictionary is desired.

### Used with cli_parse_transform as a transform

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

### Used a jinja filter

```yaml
- set_fact:
    data:
      TABLE_cdp_neighbor_brief_info:
      ROW_cdp_neighbor_brief_info:
      - ifindex: '83886080'
        device_id: nxos122(9I2AP2ONMU7)
        intf_id: mgmt0
        ttl: '128'
        capability:
        - router
        - switch
        - Supports-STP-Dispute
        platform_id: N9K-9000v
        port_id: mgmt0
      - ifindex: '83886080'
        device_id: ios102.cidrblock.net
        intf_id: mgmt0
        ttl: '161'
        capability: router
        platform_id: cisco CSR1000V
        port_id: GigabitEthernet1
      - ifindex: '83886080'
        device_id: nxos103(9NL5F64YZ82)
        intf_id: mgmt0
        ttl: '128'
        capability:
        - router
        - switch
        - Supports-STP-Dispute
        platform_id: N9K-9000v
        port_id: mgmt0
      - ifindex: '83886080'
        device_id: nxos104(98C98YNOKAL)
        intf_id: mgmt0
        ttl: '128'
        capability:
        - router
        - switch
        - Supports-STP-Dispute
        platform_id: N9K-9000v
        port_id: mgmt0
    neigh_count: '4'

- debug:
    msg: "{{ data|nmake.jetpack.flatten_list_of_dicts([{'key': 'ROW_cdp_neighbor_brief_info', 'value': 'device_id'}])}}"

# result
msg:
  ROW_cdp_neighbor_brief_info:
  - nxos122(9I2AP2ONMU7)
  - ios102.cidrblock.net
  - nxos103(9NL5F64YZ82)
  - nxos104(98C98YNOKAL)
  TABLE_cdp_neighbor_brief_info: null

```
