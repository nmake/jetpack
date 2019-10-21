# Operating state

`operating_state` is an Ansible role that collects information about various resources on a network devices and returns parsed and structured data.

#### The following resources are current supported:
- arp
- cdp
- fex
- hardware
- interfaces
- lldp
- mac
- spanning_tree
- system
- version
- vlan
- vlan.private_vlan
- vpc

#### The following network operating systems are currently supported:
- ios/iosxe
- nxos
- eos

#### The following parser engines are supported:
- native_json: Use the network device's native json support
- native_xml: Use the network device's native xml support
- pyats: Use the Cisco pyats/genie library


## Quick start

```
- hosts: all
  gather_facts: false
  roles:
  - role: nmake.jetpack.gather_states
    gather_states:
    - all
  tasks:
  - debug:
      var: ansible_facts
```

# Role parameters

- `gather_states`: (required) Gather the operating state for a list of resources.  `all` will gather all available resources. Combined with `all`, `!resource` will exclude the resource.
- `gather_states_engine` (optional) Set the parsing engine for a particular network operating system.
- `fact_key` (optional) Store the gathered state information in a new root fact key.

## Use cases:

#### Only gather a specfic resource

```
- hosts: all
  gather_facts: false
  roles:
  - role: nmake.jetpack.gather_states
    gather_states:
    - interfaces
  tasks:
  - debug:
      var: ansible_facts
```

#### Gather all, excluding a specfic resource

```
- hosts: all
  gather_facts: false
  roles:
  - role: nmake.jetpack.gather_states
    gather_states:
    - all
    - !interfaces
  tasks:
  - debug:
      var: ansible_facts
```

#### Gather before and after network changes and compare

```
- hosts: all
  gather_facts: false
  tasks:
  - include_role:
      name: nmake.jetpack.gather_states
    vars:
      fact_key: before
      gather_states:
      - all
  - debug:
      msg: Make changes here
  - include_role:
      name: nmake.jetpack.gather_states
    vars:
      fact_key: after
      gather_states:
      - all

  - name: Compare the before and after in dotted format
    nmake.jetpack.fact_diff:
      before: {{ before|default({})|nmake.jetpack.to_dotted }}
      after: {{ after|default({})|nmake.jetpack.to_dotted }}
```
