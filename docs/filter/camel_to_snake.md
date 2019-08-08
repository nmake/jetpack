## `camel_to_snake` 

Basic camelCase to snake_case conversion. This is useful for `eos` because `eos` return keys in camelCase format.

    ```yaml
    # before
    - cli_parse_transform:
        engine: native_json
          commands:
          - command: show interface
            set_fact: True

    ansible_facts:
      interfaces:
        Ethernet1:
          autoNegotiate: unknown
          bandwidth: 0
          burnedInAddress: 52:54:00:1b:da:be

    # after
    - cli_parse_transform:
        engine: native_json
          commands:
          - command: show interface
            set_fact: True
            transform:
            - name: camel_to_snake

    ansible_facts:
      interfaces:
        Ethernet1:
          auto_negotiate: unknown
          bandwidth: 0
          burned_in_address: 52:54:00:1b:da:be
    ```
