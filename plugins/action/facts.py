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
import subprocess

from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    """Gather facts relating to the Ansible inventory"""

    TRANSFERS_FILES = False
    _requires_connection = False
    _supports_check_mode = True
    _supports_async = False

    def get_vars_files(self, vars_path, task_vars):
        matches = []

        config_lookup = self._shared_loader_obj.lookup_loader.get(
            'ansible.builtin.config',
            loader=self._loader,
            templar=self._templar
        )
        exts = config_lookup.run(
            ['YAML_FILENAME_EXTENSIONS'], variables=task_vars
        )[0]
        exts.append('')  # INI files may have no extension

        if vars_path.is_dir():
            self._display.vv(f"Searching directory: {vars_path}")
            for vars_file_path in vars_path.iterdir():
                if vars_file_path.is_file() and vars_file_path.suffix in exts:
                    matches.append(str(vars_file_path))

        for ext in exts:
            candidate = Path(str(vars_path) + ext)
            if candidate.is_file():
                if vars_path.is_dir():
                    self._display.warning(
                        f'Vars file "{candidate}" will be ignored because '
                        f'directory "{vars_path}" exists'
                    )
                else:
                    matches.append(str(candidate))

        return matches

    def get_inv(self, task_vars=None):
        task_vars = task_vars or {}

        hostname = task_vars.get('inventory_hostname', 'localhost')
        inv_facts = {'name': hostname}
        self._display.v("Collecting inventory facts...")

        inv_file_path = Path(
            task_vars.get('inventory_file') or '/etc/ansible/hosts'
        )
        inv_facts['path'] = str(inv_file_path)
        inv_dir_path = inv_file_path.parent
        self._display.vv(f"Inventory file: {inv_file_path}")

        try:
            result = subprocess.run(
                ['file', '-b', '--', str(inv_file_path)],
                capture_output=True,
                encoding='utf-8',
                check=True
            )
            inv_facts['exec'] = 'executable' in result.stdout
        except Exception as err:
            self._display.warning(
                f'Unable to determine if {inv_file_path} is executable on '
                f"{hostname}: {err}"
            )

        # host_vars
        host_vars_path = inv_dir_path / 'host_vars' / hostname
        inv_facts['vars_paths'] = self.get_vars_files(
            vars_path=host_vars_path,
            task_vars=task_vars
        )

        # group_vars
        groups = list(task_vars.get('group_names', [])) + ['all']
        inv_facts['groups'] = groups
        group_vars_dir = inv_dir_path / 'group_vars'
        for group in groups:
            group_vars_path = group_vars_dir / group
            inv_facts['vars_paths'] += self.get_vars_files(
                vars_path=group_vars_path,
                task_vars=task_vars
            )

        return inv_facts

    def run(self, tmp=None, task_vars=None):
        task_vars = task_vars or {}
        tmp = None  # no longer used in modern Ansible

        argument_spec = {}
        self.validate_argument_spec(argument_spec=argument_spec)

        result = super().run(tmp, task_vars)
        result.update({
            'ansible_facts': {
                'o0_inventory': self.get_inv(task_vars=task_vars)
            }
        })

        return result
