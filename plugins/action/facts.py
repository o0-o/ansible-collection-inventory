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
from typing import Any, Dict, List, Optional

from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    """Gather facts relating to the Ansible inventory.

    This action plugin collects information about the Ansible inventory
    including inventory file details, host and group variable paths,
    and inventory structure. Since it operates on the controller host,
    it does not require a connection to remote hosts.

    The plugin discovers host_vars and group_vars directories relative
    to the inventory file and identifies all variable files that would
    be loaded for the current host.

    .. note::
       This plugin operates locally on the controller and does not
       require a connection to remote hosts.
    """

    TRANSFERS_FILES = False
    _requires_connection = False
    _supports_check_mode = True
    _supports_async = False
    _supports_diff = False

    def get_vars_files(
        self, vars_path: Path, task_vars: Dict[str, Any]
    ) -> List[str]:
        """Get list of variable files for a given path.

        Searches for variable files with supported extensions in the
        specified path, supporting both files and directories.

        :param Path vars_path: Path to search for variable files
        :param Dict[str, Any] task_vars: Task variables dictionary
        :returns List[str]: List of variable file paths that would be
            loaded by Ansible

        .. note::
           This method uses the YAML_FILENAME_EXTENSIONS configuration
           to determine which file extensions are considered valid.
        """
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

    def get_inv(self, task_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collect comprehensive inventory information.

        Gathers details about the inventory file, determines if it's
        executable, and discovers all host_vars and group_vars files
        that apply to the current host.

        :param Optional[Dict[str, Any]] task_vars: Task variables dictionary
        :returns Dict[str, Any]: Inventory information including file path,
            variable paths, and group membership

        .. note::
           This method uses the 'file' command to determine if the
           inventory file is executable (dynamic inventory).
        """
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

    def run(
        self, tmp: Optional[str] = None, task_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main entry point for the inventory facts action plugin.

        Gathers facts about the Ansible inventory and returns them under
        the o0_inventory fact namespace.

        :param Optional[str] tmp: Temporary directory path (unused)
        :param Optional[Dict[str, Any]] task_vars: Task variables dictionary
        :returns Dict[str, Any]: Standard Ansible result dictionary

        .. note::
           This method operates locally on the controller host and does
           not require a connection to remote hosts. It warns when not
           run with run_once: true.
        """
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
