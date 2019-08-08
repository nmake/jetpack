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
- set_fact:
    data:
      TABLE_interface:
        ROW_interface:
          interface: mgmt0
          state: up
          eth_hw_desc: Ethernet
          eth_hw_addr: 5254.00a0.a2ff
          eth_bia_addr: 5254.00a0.a2ff
          eth_ip_addr: 192.168.101.14
          eth_ip_mask: '24'
          eth_ip_prefix: 192.168.101.0
          eth_mtu: '1500'
          eth_bw: '1000000'
          eth_dly: '10'
          eth_reliability: '161'
          eth_txload: '1'
          eth_rxload: '1'
          encapsulation: ARPA
          eth_duplex: full
          eth_speed: 1000 Mb/s
          eth_autoneg: 'on'
          eth_mdix: 'off'
          eth_ethertype: '0x0000'
          vdc_lvl_in_avg_bits: '1352'
          vdc_lvl_in_avg_pkts: '1'
          vdc_lvl_out_avg_bits: '2040'
          vdc_lvl_out_avg_pkts: '1'
          vdc_lvl_in_pkts: '247389'
          vdc_lvl_in_ucast: '62555'
          vdc_lvl_in_mcast: '184546'
          vdc_lvl_in_bcast: '288'
          vdc_lvl_in_bytes: '20772264'
          vdc_lvl_out_pkts: '121462'
          vdc_lvl_out_ucast: '115902'
          vdc_lvl_out_mcast: '5557'
          vdc_lvl_out_bcast: '3'
          vdc_lvl_out_bytes: '50090452'


- name: Convert string to native type where possible
  debug:
    msg: "{{ data|nmake.jetpack.str_to_native }}"

# result
msg:
 TABLE_interface:
   ROW_interface:
     encapsulation: ARPA
     eth_autoneg: 'on'
     eth_bia_addr: 5254.00a0.a2ff
     eth_bw: 1000000
     eth_dly: 10
     eth_duplex: full
     eth_ethertype: 0
     eth_hw_addr: 5254.00a0.a2ff
     eth_hw_desc: Ethernet
     eth_ip_addr: 192.168.101.14
     eth_ip_mask: 24
     eth_ip_prefix: 192.168.101.0
     eth_mdix: 'off'
     eth_mtu: 1500
     eth_reliability: 161
     eth_rxload: 1
     eth_speed: 1000 Mb/s
     eth_txload: 1
     interface: mgmt0
     state: up
     vdc_lvl_in_avg_bits: 1352
     vdc_lvl_in_avg_pkts: 1
     vdc_lvl_in_bcast: 288
     vdc_lvl_in_bytes: 20772264
     vdc_lvl_in_mcast: 184546
     vdc_lvl_in_pkts: 247389
     vdc_lvl_in_ucast: 62555
     vdc_lvl_out_avg_bits: 2040
     vdc_lvl_out_avg_pkts: 1
     vdc_lvl_out_bcast: 3
     vdc_lvl_out_bytes: 50090452
     vdc_lvl_out_mcast: 5557
     vdc_lvl_out_pkts: 121462
     vdc_lvl_out_ucast: 115902

```
