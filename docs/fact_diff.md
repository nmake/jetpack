# Fact diff

`fact_diff` is an Ansible module that compares and shows the differences between two facts. When using the default callback, differences are shown during the playbook run.  Differences are also returned from the task in the `diff_lines` key.  The task will return `changed` if the before and after are not equal.

## Quick start

```yaml
- hosts: nxos101
  gather_facts: false
  collections:
  - nmake.jetpack
  tasks:
  - cli_command:
      command: show run interface
    register: before
  - cli_config:
      config: |
        interface eth1/128
        description {{ 99999999 | random | to_uuid }}
  - cli_command:
      command: show run interface
    register: after
  - name: Show the differences between the before and after
    fact_diff:
      before: "{{ before['stdout'] }}"
      after: "{{ after['stdout'] }}"
    register: output
  - debug:
      var: output['diff_lines']
```

```diff
TASK [fact_diff] ***********************************
--- before
+++ after
@@ -1,6 +1,6 @@
 !Command: show running-config interface
-!Running configuration last done at: Tue Aug  6 16:35:47 2019
-!Time: Tue Aug  6 16:36:49 2019
+!Running configuration last done at: Tue Aug  6 16:36:53 2019
+!Time: Tue Aug  6 16:36:54 2019

 version 9.2(2) Bios:version

@@ -259,7 +259,7 @@
 interface Ethernet1/127

 interface Ethernet1/128
-  description d1b8ea5b-cf85-5434-a0f8-d10ca362d452
+  description 618839f3-06be-54b1-b066-0de2c6617b26
   no switchport
   no ip redirects
   ip address 192.168.1.1/24 route-preference 2 tag 5

changed: [nxos101]
```

## Making comparisons using different formats

By default, each fact is serialized to json prior to the comparison. Changing the format of the facts as they are passed off to the module can make identifying the changes easier.

The `to_dotted` filter plugin becomes useful to identify changes that may be deeply nested within the fact.

```
- hosts: nxos101
  gather_facts: false
  collections:
  - nmake.jetpack
  tasks:
  - name: Show the difference as json (default)
    fact_diff:
      before: {}
      after: "{{ hostvars[inventory_hostname] }}"
  - name: Show the difference as yaml
    fact_diff:
      before: {}
      after: "{{ hostvars[inventory_hostname]|to_nice_yaml }}"
  - name: Show the difference as dotted
    fact_diff:
      before: {}
      after: "{{ hostvars[inventory_hostname]|nmake.jetpack.to_dotted }}"
  - name: Show the difference as dotted yaml
    fact_diff:
      before: {}
      after: "{{ hostvars[inventory_hostname]|nmake.jetpack.to_dotted|to_nice_yaml }}"
```

See the examples directory for additional examples.
