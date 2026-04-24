# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""FreeCAD GUI registration for the AI Agent Sidebar."""

from __future__ import annotations

import builtins

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


class _AIAgentSidebarWorkbenchMixin:
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


def _find_freecad_workbench_base() -> type | None:
    base = globals().get("Workbench") or getattr(builtins, "Workbench", None)
    return base if isinstance(base, type) else None


def build_workbench_class(base_class: type | None = None) -> type:
    """Create a FreeCAD-compatible workbench class.

    FreeCADGui.addWorkbench requires an instance whose class inherits the
    built-in Workbench base. That base is only present inside FreeCAD, so tests
    use object as the fallback base.
    """

    base = base_class or _find_freecad_workbench_base() or object
    return type("AIAgentSidebarWorkbench", (_AIAgentSidebarWorkbenchMixin, base), {})


AIAgentSidebarWorkbench = build_workbench_class()


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
        FreeCADGui.addWorkbench(build_workbench_class()())
        _WORKBENCH_REGISTERED = True


register()
