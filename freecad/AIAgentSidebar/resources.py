# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Packaged resource helpers."""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path


def icon_path(name: str = "Logo.svg") -> str:
    resource = files("freecad.AIAgentSidebar") / "Resources" / "Icons" / name
    with as_file(resource) as path:
        return str(Path(path))
