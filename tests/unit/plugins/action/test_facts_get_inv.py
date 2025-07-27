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

import subprocess
from pathlib import Path


def test_get_inv(monkeypatch, action_base) -> None:
    """Test get_inv collects inventory facts correctly."""
    tmp_dir = Path('/tmp/test-inventory')
    inv_file = tmp_dir / 'hosts'
    host_vars_file = tmp_dir / 'host_vars/testhost.yml'
    group_vars_file = tmp_dir / 'group_vars/testgroup.yml'

    # Simulate filesystem
    monkeypatch.setattr(
        Path, 'is_file', lambda self: self.name.endswith('.yml')
    )
    monkeypatch.setattr(
        Path, 'is_dir', lambda self: not self.name.endswith('.yml')
    )
    monkeypatch.setattr(
        Path, 'iterdir', lambda self: [host_vars_file, group_vars_file]
    )

    class DummyCompletedProcess:
        def __init__(self, stdout: str):
            self.stdout = stdout
            self.stderr = ''
            self.returncode = 0

    def mock_run(*args, **kwargs):
        return DummyCompletedProcess(stdout="ASCII text")  # simulate non-executable

    monkeypatch.setattr(subprocess, 'run', mock_run)

    # Mock config lookup plugin to return extensions
    class DummyLookup:
        def run(self, terms, variables=None, **kwargs):
            return [['.yml']]

    action_base._shared_loader_obj.lookup_loader.get.return_value = (
        DummyLookup()
    )

    task_vars = {
        'inventory_hostname': 'testhost',
        'inventory_file': str(inv_file),
        'group_names': ['testgroup']
    }

    facts = action_base.get_inv(task_vars=task_vars)

    assert facts['name'] == 'testhost'
    assert facts['path'] == str(inv_file)
    assert 'testgroup' in facts['groups']
    assert 'all' in facts['groups']
    assert host_vars_file.name in [Path(p).name for p in facts['vars_paths']]
    assert group_vars_file.name in [Path(p).name for p in facts['vars_paths']]
    assert 'exec' in facts, f"exec key missing in facts: {facts}"
    assert facts['exec'] is False
