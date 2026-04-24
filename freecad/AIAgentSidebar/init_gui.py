# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""FreeCAD GUI registration for the AI Agent Sidebar."""

from __future__ import annotations

from . import COMMAND_NAME
from .resources import icon_path
from .sidebar import open_sidebar

_REGISTERED = False
_WORKBENCH_REGISTERED = False


class OpenAIAgentSidebarCommand:
    """FreeCAD command that opens or focuses the sidebar dock."""

    def GetResources(self):  # noqa: N802 - FreeCAD API naming
        return {
            "MenuText": "Open AI Agent Sidebar",
            "ToolTip": "Open the dockable AI Agent Sidebar.",
            "Pixmap": icon_path(),
        }

    def Activated(self):  # noqa: N802 - FreeCAD API naming
        open_sidebar()

    def IsActive(self):  # noqa: N802 - FreeCAD API naming
        return True


class AIAgentSidebarWorkbench:
    """Small workbench that exposes the sidebar command as a button."""

    MenuText = "AI Agent Sidebar"
    ToolTip = "Open the AI Agent Sidebar dock."
    Icon = icon_path()

    def Initialize(self):  # noqa: N802 - FreeCAD API naming
        commands = [COMMAND_NAME]
        self.appendToolbar("AI Agent Sidebar", commands)
        self.appendMenu("AI Agent Sidebar", commands)

    def Activated(self):  # noqa: N802 - FreeCAD API naming
        pass

    def Deactivated(self):  # noqa: N802 - FreeCAD API naming
        pass

    def GetClassName(self):  # noqa: N802 - FreeCAD API naming
        return "Gui::PythonWorkbench"


def register() -> None:
    global _REGISTERED, _WORKBENCH_REGISTERED
    if _REGISTERED and _WORKBENCH_REGISTERED:
        return

    try:
        import FreeCADGui  # type: ignore
    except ImportError:
        return

    if not _REGISTERED:
        FreeCADGui.addCommand(COMMAND_NAME, OpenAIAgentSidebarCommand())
        _REGISTERED = True

    if not _WORKBENCH_REGISTERED and hasattr(FreeCADGui, "addWorkbench"):
        FreeCADGui.addWorkbench(AIAgentSidebarWorkbench())
        _WORKBENCH_REGISTERED = True


register()
