# Operating state

`operating_state` is an Ansible role that collects information about various resources on a network devices and returns parsed and structured data.

The following resources are current supported:
- arp
- cdp
- lldp
- interfaces
- system
- spanning_tree

The following network operating systems are currently supported:
- ios/iosxe
- nxos
- eos

The following parser engines are supported:
- native_json: Use the network device's native json support
- native_xml: Use the network device's native xml support
- pyats: Use the Cisco pyats/genie library


## Quick start

```
- hosts: all
  gather_facts: false
  roles:
  - role: nmake.jetpack.operating_state
    gather_state:
    - all
  tasks:
  - debug:
      var: ansible_facts
```

# Module parameters

- `gather_state`: (required) Gather the operating state for a list of resources.  `all` will gather all available resources. Combined with `all`, `!resource` will exclude the resource.
- `xxx_engine` (optional) Set the parsing engine for a particular network operating system.
- `fact_key` (optional) Store the gathered state information in a new root fact key.
-
## Use cases:

#### Only gather a specfic resource

```
- hosts: all
  gather_facts: false
  roles:
  - role: nmake.jetpack.operating_state
    gather_state:
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
  - role: nmake.jetpack.operating_state
    gather_state:
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
      name: nmake.jetpack.operating_state
    vars:
      fact_key: before
      gather_state:
      - all
  - debug:
      msg: Make changes here
  - include_role:
      name: nmake.jetpack.operating_state
    vars:
      fact_key: after
      gather_state:
      - all
      
  - name: Compare the before and after in dotted format
    nmake.jetpack.fact_diff:
      before: "{{ before|default({})|nmake.jetpack.to_dotted }}"
      after: "{{ after|default({})|nmake.jetpack.to_dotted }}"
```
