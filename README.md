# Jetpack

Jetpack is an Ansible collection containing useful Ansible add-ons for network engineers and operators.

## Compatibility

Ansible 2.9 required.

## Callback plugins

[`network_change_log`](network_change_log.md): Shows network device changes during a playbook run as well as a per-device summary of changes when the playbook completes.

## Modules

[`cli_parse_transform`](cli_parse_transform.md): An Ansible module that combines the running of commands on a network device with the parsing and transformation of the resulting structured data. Use either `pyats` or the device's `native_json` support for parsing.
