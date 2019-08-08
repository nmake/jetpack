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

```
