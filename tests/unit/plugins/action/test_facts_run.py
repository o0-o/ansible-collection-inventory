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

from __future__ import annotations

from pathlib import Path


def test_run_inventory_facts(monkeypatch, action_base) -> None:
    """Test run returns valid ansible_facts structure."""
    # Stub out file/directory and vars lookup logic
    monkeypatch.setattr(Path, 'is_file', lambda self: False)
    monkeypatch.setattr(Path, 'is_dir', lambda self: False)

    monkeypatch.setattr(
        action_base, 'get_vars_files',
        lambda vars_path, task_vars: []
    )

    # Run with minimal viable task_vars
    task_vars = {
        'inventory_hostname': 'localhost',
        'group_names': ['ungrouped'],
        'inventory_file': '/etc/ansible/hosts'
    }

    action_base._task.run_once = True
    action_base._task.async_val = False
    result = action_base.run(task_vars=task_vars)

    facts = result['ansible_facts']['o0_inventory']

    assert facts['name'] == 'localhost'
    assert facts['path'] == '/etc/ansible/hosts'
    assert facts['groups'] == ['ungrouped', 'all']
    assert isinstance(facts['vars_paths'], list)
