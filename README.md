# Ansible Collection - o0_o.inventory

Documentation for the collection.# o0_o.inventory.facts

Collect facts about the current inventory source and structure.

## Overview

The `o0_o.inventory.facts` action plugin gathers metadata related to the
inventory being used in an Ansible run. It is designed to expose useful
information for debugging, introspection, or dynamic behavior based on
inventory layout.

Unlike host facts, this plugin returns facts about the *inventory system*
itself — such as the inventory file path, associated vars files, group
membership, and whether the inventory file is an executable script.

## Returned Facts

The plugin returns a dictionary under the `o0_inventory` namespace.
Example structure:

```yaml
o0_inventory:
  name: testhost
  path: /etc/ansible/hosts
  exec: false
  vars_paths:
    - /etc/ansible/host_vars/testhost.yml
    - /etc/ansible/group_vars/all.yml
  groups:
    - web
    - all
```

## Field Descriptions

- name: Inventory hostname (inventory_hostname).
- path: Full path to the active inventory source.
- exec: Boolean indicating whether the inventory source is executable.
- vars_paths: List of detected host_vars and group_vars files.
- groups: List of groups the host belongs to, including all.

## Platform Support

- Works on any controller with Python and the file utility installed.
- No Python is required on the managed nodes.

## Compatibility

- Check mode supported
- Async not supported
- Platform: POSIX (controller only)

## Use Case

- This plugin is helpful for roles or collections that need to:
- Adjust behavior based on inventory source (e.g. file vs script).
- Validate inventory structure (e.g. missing vars files).
- Dynamically discover related vars files.
- Troubleshoot group membership or file resolution.

## Example Use

```yaml
- name: Gather inventory facts
  o0_o.inventory.facts:

- name: Debug inventory file path
  debug:
    var: o0_inventory['path']
```

## Development

This collection follows the same structure and contribution guidelines as [`o0_o.posix`](https://galaxy.ansible.com/o0_o/posix). All source code is hosted at:

**GitHub**: [https://github.com/o0-o/ansible-collection-inventory](https://github.com/o0-o/ansible-collection-inventory)

Pull requests and issues welcome.

## License

[GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.txt)

---

© 2025 oØ.o (@o0-o)
