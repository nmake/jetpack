## `keep_keys`

Provide a list of keys to keep. Comparisons are limited to keys that have a value which is a string, integer, or boolean.  The keys are used as regular expressions. This is useful if the facts need to be limited to only a few specific keys.

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
      - name: keep_keys
        keys:
        - interface
        - admin_state
        - ^state$

ansible_facts:
   TABLE_interface:
     ROW_interface:
     - admin_state: down
       interface: Ethernet1/1
       state: down
     - admin_state: up
       interface: Ethernet1/2
       state: up

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
    msg: "{{ data|nmake.jetpack.keep_keys(['state', 'type', 'interface']) }}"

# result
msg:
  ROW_interface:
  - interface: Ethernet1/1
    state: connected
    type: 10g
  - interface: Ethernet1/2
    state: connected
    type: 10g

```
