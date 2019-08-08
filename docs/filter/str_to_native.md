## `str_to_native`

Convert values to their native types.  `ast.literal_eval(parsed)` is used for the converstion, in addition, "none", "true", and "false" will be converted to `None`, `True` and `False` respectively.  This is useful when integers, booleans, etc are returned as strings and they should be converted to their respective type.

### Used with cli_parse_transform as a transform

```yaml

- cli_parse_transform:
    engine: native_json
    commands:
    - command: show interface counters
      set_fact: True

ansible_facts:
  TABLE_rx_counters:
    ROW_rx_counters:
    - eth_inpkts: '163243498'
      eth_inucast: '393236'
      interface_rx: mgmt0

- cli_parse_transform:
    engine: native_json
    commands:
    - command: sho interface counters
      set_fact: True
      transform:
      - name: str_to_native

ansible_facts:
  TABLE_rx_counters:
    ROW_rx_counters:
    - eth_inpkts: 163246414
      eth_inucast: 393265
      interface_rx: mgmt0

```

### Used a jinja filter

```yaml

```
