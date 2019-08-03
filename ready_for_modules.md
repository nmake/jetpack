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

#### Split inventory data into multiple dictionaries, one per module

```
tasks:
- ready_for_modules:
    modules:
    - name: junos_interfaces
      data:
        config: "{{ interfaces }}"
    - name: junos_l3_interfaces
      data:
        config: "{{ interfaces }}"
  register: result
- debug:
    var: result['ready']['junos_interfaces']
- debug:
    var: result['ready']['junos_l3_interfaces']
```

#### Manipulate the inventory as it is passed

```
- hosts: eos
  gather_facts: False
  collections:
  - nmake.jetpack
  vars:
    hostconfig:
      host_name: vyos01
      description: Virtual appliance for module testing
      version: VyOS 1.2.0-rolling+201905140337
      domain_name: test.example.com
      domain_search:
      - sub1.example.com
      - sub2.example.com
      name_servers:
      - 8.8.8.8
      - 8.8.4.4
      interfaces:
        Eth2:
          name: eth2
          description: 'Configured by Ansible'
          enabled: True
          metadata:
            int_type: trunk port
            last_change: 9/3/2019
            notes:
            - 9/3/2019, description updated BT
          vifs:
            - vlan_id: 200
              description: "VIF 200 - ETH2"
        Eth3:
          description: 'Configured by Ansible'
          mtu: 1500


  tasks:
  - ready_for_modules:
      modules:
      - name: vyos_system
        data: "{{ hostconfig }}"
      - name: vyos_interfaces
        data:
          config: "{{ hostconfig.interfaces.values() | list }}"
    register: result

  - debug:
      var: result
```


See the examples directory for additional examples.
