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

from typing import Generator
from unittest.mock import MagicMock

import pytest

from ansible_collections.o0_o.inventory.plugins.action.facts import (
    ActionModule,
)


@pytest.fixture
def action_base() -> Generator[ActionModule, None, None]:
    """Provide a mock-initialized ActionModule for unit testing."""
    return ActionModule(
        task=MagicMock(),
        connection=MagicMock(),
        play_context=MagicMock(),
        loader=MagicMock(),
        templar=MagicMock(),
        shared_loader_obj=MagicMock(),
    )
