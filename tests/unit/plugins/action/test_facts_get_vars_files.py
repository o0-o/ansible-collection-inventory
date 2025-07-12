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
import types


def test_get_vars_files_with_dir(monkeypatch, action_base):
    """
    Verify that get_vars_files() collects valid files from a vars directory
    with appropriate YAML extensions defined by the config plugin.
    """
    # Fake file names in the directory
    fake_dir = Path('/tmp/vars/host_vars/myhost')
    fake_entries = [
        fake_dir / 'foo.yml',
        fake_dir / 'bar.yaml',
        fake_dir / 'baz.txt',
    ]

    # Patch Path.iterdir to return fake entries
    monkeypatch.setattr(Path, 'iterdir', lambda self: fake_entries)

    # Patch Path.is_dir to return True for the directory
    monkeypatch.setattr(Path, 'is_dir', lambda self: self == fake_dir)

    # Patch Path.is_file to match known files
    monkeypatch.setattr(
        Path,
        'is_file',
        lambda self: self.name in ['foo.yml', 'bar.yaml']
    )

    # Mock config plugin to return .yml/.yaml extensions
    mock_lookup = types.SimpleNamespace()
    mock_lookup.run = lambda args, variables=None: [['.yml', '.yaml']]
    monkeypatch.setattr(
        action_base._shared_loader_obj.lookup_loader,
        'get',
        lambda name, **kwargs: mock_lookup
    )

    matches = action_base.get_vars_files(fake_dir, task_vars={})

    assert '/tmp/vars/host_vars/myhost/foo.yml' in matches
    assert '/tmp/vars/host_vars/myhost/bar.yaml' in matches
    assert not any('baz.txt' in m for m in matches)


def test_get_vars_files_with_file(monkeypatch, action_base):
    """
    Verify that get_vars_files() detects single vars files with matching
    extensions and warns when a directory exists at the same path.
    """
    path_with_ext = Path('/tmp/vars/host_vars/myhost.yml')
    fake_path = Path('/tmp/vars/host_vars/myhost')

    # Patch is_dir to return False for the file path
    monkeypatch.setattr(Path, 'is_dir', lambda self: False)

    # Patch is_file to return True only for the .yml file
    monkeypatch.setattr(
        Path,
        'is_file',
        lambda self: self == path_with_ext
    )

    # Mock config plugin to return .yml as valid extension
    mock_lookup = types.SimpleNamespace()
    mock_lookup.run = lambda args, variables=None: [['.yml']]
    monkeypatch.setattr(
        action_base._shared_loader_obj.lookup_loader,
        'get',
        lambda name, **kwargs: mock_lookup
    )

    matches = action_base.get_vars_files(path_with_ext, task_vars={})

    assert '/tmp/vars/host_vars/myhost.yml' in matches
