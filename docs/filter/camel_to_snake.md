## `camel_to_snake`

Basic camelCase to snake_case conversion. This is useful for `eos` because `eos` return keys in camelCase format.

### Used with cli_parse_transform as a transform

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

### Used a jinja filter

```yaml
- set_fact:
    data:
      uptime: 328049.91
      modelName: "vEOS"
      internalVersion: "4.21.1.1F-10146868.42111F"
      systemMacAddress: "52:54:00:21:fd:8f"
      serialNumber: ""
      memTotal: 2016548
      bootupTimestamp: 1564950373.0
      memFree: 1372072
      version: "4.21.1.1F"
      architecture: "i386"
      isIntlVersion: false
      internalBuildId: "ed3973a9-79db-4acc-b9ac-19b9622d23e2"
      hardwareRevision: ""

- debug:
    msg: "{{ data|nmake.jetpack.camel_to_snake }}"

# result
msg:
  architecture: i386
  bootup_timestamp: 1564950373.0
  hardware_revision: ''
  internal_build_id: ed3973a9-79db-4acc-b9ac-19b9622d23e2
  internal_version: 4.21.1.1F-10146868.42111F
  is_intl_version: false
  mem_free: 1372072
  mem_total: 2016548
  model_name: vEOS
  serial_number: ''
  system_mac_address: 52:54:00:21:fd:8f
  uptime: 328049.91
  version: 4.21.1.1F

```
