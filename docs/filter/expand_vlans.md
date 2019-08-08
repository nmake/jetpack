
## `expand_vlans`

Expand vlans in range syntax into a list. This is useful when there is a need to `assert` that a vlan in allowed in a trunk later in the playbook.

    ```yaml

    # before
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Ethernet1 switchport
          set_fact: True

    switchports:
      Ethernet1:
        enabled: true
        switchportInfo:
          trunkAllowedVlans: 1-3

    # after
    - cli_parse_transform:
        engine: native_json
        commands:
        - command: show interface Ethernet1 switchport
          set_fact: True
          transform:
          - name: expand_vlans
            keys:
            - trunkAllowedVlans

    switchports:
      Ethernet1:
        enabled: true
        switchportInfo:
          trunkAllowedVlans:
          - '1'
          - '2'
          - '3'
    ```
