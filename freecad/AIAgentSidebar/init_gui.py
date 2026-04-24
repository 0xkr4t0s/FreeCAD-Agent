# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""FreeCAD GUI registration for the AI Agent Sidebar."""

from __future__ import annotations

from . import COMMAND_NAME
from .sidebar import open_sidebar

_REGISTERED = False


class OpenAIAgentSidebarCommand:
    """FreeCAD command that opens or focuses the sidebar dock."""

    def GetResources(self):  # noqa: N802 - FreeCAD API naming
        return {
            "MenuText": "Open AI Agent Sidebar",
            "ToolTip": "Open the dockable AI Agent Sidebar.",
            "Pixmap": "",
        }

    def Activated(self):  # noqa: N802 - FreeCAD API naming
        open_sidebar()

    def IsActive(self):  # noqa: N802 - FreeCAD API naming
        return True


def register() -> None:
    global _REGISTERED
    if _REGISTERED:
        return

    try:
        import FreeCADGui  # type: ignore
    except ImportError:
        return

    FreeCADGui.addCommand(COMMAND_NAME, OpenAIAgentSidebarCommand())
    _REGISTERED = True


register()
