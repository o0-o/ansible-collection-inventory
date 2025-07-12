# vim: ts=4:sw=4:sts=4:et:ft=python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
#
# GNU General Public License v3.0+
# SPDX-License-Identifier: GPL-3.0-or-later
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Copyright (c) 2025 oØ.o (@o0-o)
#
# This file is part of the o0_o.inventory Ansible Collection.

DOCUMENTATION = r'''
---
module: facts
short_description: Gather facts related to the Ansible inventory
description:
  - This module runs on the Ansible controller to inspect inventory-related
    information for the current play target, including its defined groups,
    the inventory file path, and host/group variable file resolution paths.
  - Designed to support custom dynamic behaviors based on inventory layout.
author:
  - oØ.o (@o0-o)
attributes:
  check_mode:
    description: This module supports check mode.
    support: full
  async:
    description: This module does not support async operation.
    support: none
  platform:
    description: Only POSIX platforms are supported.
    support: full
    platforms: posix
'''

EXAMPLES = r'''
- name: Gather inventory facts
  o0_o.inventory.facts:

- name: Show inventory file path
  debug:
    msg: "Inventory path: {{ o0_inventory['path'] }}"
'''

RETURN = r'''
ansible_facts:
  description: Inventory-related facts from the controller.
  returned: always
  type: dict
  contains:
    o0_inventory:
      description: Inventory facts collected for the current target
      type: dict
      contains:
        name:
          description: Inventory hostname of the current play target
          type: str
        path:
          description: Resolved inventory file path
          type: str
        exec:
          description: Whether the inventory source is marked as executable
          type: bool
          returned: when determinable
        groups:
          description: List of groups the host belongs to (plus "all")
          type: list
          elements: str
        vars_paths:
          description: Paths to applicable host/group variable files
          type: list
          elements: str
'''
