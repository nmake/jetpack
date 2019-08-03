# Ready for modules

`ready_for_modules` is an Ansible module that compares structured data to what an Ansible module expects and removes the extranious information.  It can also be used to split a single dictionary into multiple dictionaries, one for each module desired.

Note:  `ready_for_modules` is only as good as the documentation for a given module. Please run in check mode to ensure the data is intact. 

## Quick start

```
- hosts: eos
  gather_facts: False
  collections:
  - nmake.jetpack
  vars:
    interfaces:
    - name: connection to lx12345
      description: 'Configured and Merged by Ansible Network'
      enabled: True
      metadata:
        int_type: host port
        last_changed: 9/3/2020
        changed_by: Brad Thornton
    - name: GigabitEthernet0/3
      description: connection to rhv12345
      mtu: 2800
      enabled: False
      speed: 100
      duplex: full
      metadata:
        int_type: rhv uplink
        last_changed: 9/3/2020
        changed_by: Brad Thornton
  tasks:
  - ready_for_modules:
      modules:
      - name: ios_interfaces
        data:
          config: "{{ interfaces }}"
    register: result
  - debug:
      var: result

# result

ready:
  ios_interfaces:
    config:
    - description: Configured and Merged by Ansible Network
      enabled: true
      name: connection to lx12345
    - description: connection to rhv12345
      duplex: full
      enabled: false
      mtu: 2800
      name: GigabitEthernet0/3
      speed: 100
```

## Use cases:

#### Removing extra or meta data from an inventory

Simply provide the data to `ready_for_modules` along with the module name.  The module's docuementation is used to remove extra key value pairs form the data.  The resulting data will be ready for use with the module.

```
- ready_for_modules:
    modules:
    - name: ios_interfaces
      data:
        config: "{{ interfaces }}"
  register: result

- ios_interfaces:
    config: "{{ result.ready.ios_interfaces.config }}"
```
