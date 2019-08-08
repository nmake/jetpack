## `unnest`

Move a dictionary up one level in the tree. This is useful when the parsed data is unneccesarily complex.

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
