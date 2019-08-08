## `replace_keys`

Change the name of keys in the data. The before value is used as a regex. This is useful to modify the output of one command to look like another.

### Used with cli_parse_transform as a transform

```yaml

# before
- cli_parse_transform:
    engine: native_json
    commands:
    - command: show ip interface
      set_fact: True

ansible_facts:
   TABLE_intf:
     ROW_intf:
       <...>
       dir-bcast: disabled
       icmp-redirect: disabled
       intf-name: Ethernet1/128
       iod: '132'

# after
- cli_parse_transform:
    engine: native_json
    commands:
    - command: show ip interface
      set_fact: True
      transform:
      - name: replace_keys
        keys:
        - before: intf-name
          after: interface

ansible_facts:
  TABLE_intf:
    ROW_intf:
      <...>
      dir-bcast: disabled
      icmp-redirect: disabled
      interface: Ethernet1/128
      iod: '132'

```

### Used a jinja filter

```yaml
- set_fact:
    data:
      TABLE_intf:
        ROW_intf:
          vrf-name-out: default
          intf-name: Eth1/128
          proto-state: down
          link-state: down
          admin-state: down
          iod: '132'
          prefix: 192.168.1.1
          ip-disabled: 'FALSE'

- name: Change the intf-name key to interface
  debug:
    msg: "{{ data|nmake.jetpack.replace_keys([{'before': 'intf-name', 'after': 'interface'}]) }}"

- name: Replace the dashes with underscore
  debug:
    msg: "{{ data|nmake.jetpack.replace_keys([{'before': '-', 'after': '_'}]) }}"

# result
msg:
  TABLE_intf:
    ROW_intf:
      admin-state: down
      interface: Eth1/128
      iod: '132'
      ip-disabled: 'FALSE'
      link-state: down
      prefix: 192.168.1.1
      proto-state: down
      vrf-name-out: default

msg:
   TABLE_intf:
     ROW_intf:
       admin_state: down
       intf_name: Eth1/128
       iod: '132'
       ip_disabled: 'FALSE'
       link_state: down
       prefix: 192.168.1.1
       proto_state: down
       vrf_name_out: default

```
