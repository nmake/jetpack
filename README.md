# Jetpack

Jetpack is an Ansible collection containing useful Ansible add-ons for network engineers and operators.

## Compatibility

Ansible 2.9 required.

## Callback plugins

[`network_change_log`](docs/callback/network_change_log.md): Shows network device changes during a playbook run as well as a per-device summary of changes when the playbook completes.

## Filter plugins

[`camel_to_snake`](docs/filter/camel_to_snake.md) Convert camelCase keys to snake_case keys.


## Modules

[`cli_parse_transform`](docs/module/cli_parse_transform.md): An Ansible module that combines the running of commands on a network device with the parsing and transformation of the resulting structured data. Use either `pyats` or the device's `native_json` support for parsing.

[`fact_diff`](docs/module/fact_diff.md): An Ansible module that compares and shows the differences between two facts. When using the default callback, differences are shown during the playbook run.  Differences are also returned from the task in the `diff_lines` key.  The task will return `changed` if the before and after are not equal.

[`ready_for_modules`](docs/module/ready_for_modules.md): An Ansible module that compares structured data to what an Ansible module expects and removes the extranious information.  It can also be used to split a single dictionary into multiple dictionaries, one for each module desired


### Developer notes, Note to self

As of Aug 8, two WIP changes need to be made for these to work:

https://github.com/ansible/ansible/issues/59890
https://github.com/ansible/ansible/pull/59932
