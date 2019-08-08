## `replace_keys`

Change the name of keys in the engine output. The before value is used as a regex. This is useful to modify the output of one command to look like another.

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

```
