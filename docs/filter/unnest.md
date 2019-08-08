## `unnest`

Move a dictionary up one level in the tree. This is useful when the parsed data is unneccesarily complex.

### Used with cli_parse_transform as a transform

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

### Used a jinja filter

```yaml

- set_fact:
    data:
      parent_1:
        parent_2:
          parent_3:
            lldp_neigbors:
            - ttl: 120
              neighborDevice: nxos104
              neighborPort: Ethernet1/1
              port: Ethernet1
            - ttl: 120
              neighborDevice: localhost
              neighborPort: 5254.00cd.67ab
              port: Ethernet1
            - ttl: 120
              neighborDevice: localhost
              neighborPort: 5254.00f4.f08d
              port: Ethernet1

- name: Unnest the lldp_neigbors
  debug:
    msg: "{{ data|nmake.jetpack.unnest(['parent_1', 'parent_2', 'parent_3']) }}"

# result
msg:
  lldp_neigbors:
  - neighborDevice: nxos104
    neighborPort: Ethernet1/1
    port: Ethernet1
    ttl: 120
  - neighborDevice: localhost
    neighborPort: 5254.00cd.67ab
    port: Ethernet1
    ttl: 120
  - neighborDevice: localhost
    neighborPort: 5254.00f4.f08d
    port: Ethernet1
    ttl: 120

```
