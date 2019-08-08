## `nxos_flatten_table_row`

Flatten the `TABLE...` and `ROW...` keys when using `native_json` with `nxos`.  The row name is used to generate the new root key. This is useful when using the `native_json` engine with nxos and the `TABLE` and `ROW` keys are not desired in the facts.

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
