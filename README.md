# Jetpack

Jetpack is an Ansible collection containing useful Ansible add-ons for network engineers and operators.

## Compatibility

Ansible 2.9 required.

## Callback plugins

[`network_change_log`](docs/callback/network_change_log.md): Shows network device changes during a playbook run as well as a per-device summary of changes when the playbook completes.

## Filter plugins

[`camel_to_snake`](docs/filter/camel_to_snake.md) Convert camelCase keys to snake_case keys.

[`expand_vlans`](/docs/filter/expand_vlans.md) Expand a range of vlans to a list.

[`flatten_list_of_dicts`](/docs/filter/flatten_list_of_dicts.md) Convert a list of dictionaries to a list of values.

[`keep_keys`](/docs/filter/keep_keys.md) Select which keys should be kept in the data.

[`nxos_flatten_table_row`](/docs/filter/nxos_flatten_table_row.md) Remove the nxos TABLE and ROW keys.

[`rekey_on_members`](/docs/filter/rekey_on_members.md) Turn a list of dictionaries into a dictionary based on a key.

[`replace_keys`](/docs/filter/replace_keys.md) Replace keys in the data.

[`set_root_key`](/docs/filter/set_root_key.md) Set a root key for the data.

[`stats`](/docs/filter/stats.md) Generate statistics from the data.

[`str_to_native`](/docs/filter/str_to_native.md) Convert string to their native type.

[`unnest`](/docs/filter/unnest.md) Promote a child key to it's parent in the tree.


## Modules

[`cli_parse_transform`](docs/module/cli_parse_transform.md): An Ansible module that combines the running of commands on a network device with the parsing and transformation of the resulting structured data. Use either `pyats` or the device's `native_json` support for parsing.

[`fact_diff`](docs/module/fact_diff.md): An Ansible module that compares and shows the differences between two facts. When using the default callback, differences are shown during the playbook run.  Differences are also returned from the task in the `diff_lines` key.  The task will return `changed` if the before and after are not equal.

[`ready_for_modules`](docs/module/ready_for_modules.md): An Ansible module that compares structured data to what an Ansible module expects and removes the extranious information.  It can also be used to split a single dictionary into multiple dictionaries, one for each module desired

## Roles

[`operating_state`](docs/roles/operating_state.md): An Ansible role that collects information about the operating state of various resources on a network devices and returns parsed and structured data.

## Developer notes

As of Aug 8, two WIP changes need to be made for these to work:

https://github.com/ansible/ansible/issues/59890

https://github.com/ansible/ansible/pull/59932
