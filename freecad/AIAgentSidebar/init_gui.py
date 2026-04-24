# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""FreeCAD GUI registration for the AI Agent Sidebar."""

from __future__ import annotations

from . import COMMAND_NAME
from .resources import icon_path
from .sidebar import open_sidebar
from .qt_compat import QtUnavailableError, load_qt

_REGISTERED = False
_MENU_REGISTERED = False
_MENU_ACTION = None
MENU_NAME = "AI Agent"


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


def register() -> None:
    global _REGISTERED, _MENU_REGISTERED
    if _REGISTERED and _MENU_REGISTERED:
        return

    try:
        import FreeCADGui  # type: ignore
    except ImportError:
        return

    if not _REGISTERED:
        FreeCADGui.addCommand(COMMAND_NAME, OpenAIAgentSidebarCommand())
        _REGISTERED = True

    if not _MENU_REGISTERED:
        _MENU_REGISTERED = install_menu_action(FreeCADGui)


def install_menu_action(freecad_gui) -> bool:
    """Add AI Agent > Open Sidebar to the global FreeCAD menu bar."""

    global _MENU_ACTION

    try:
        qt = load_qt()
    except QtUnavailableError:
        return False

    main_window = freecad_gui.getMainWindow()
    if main_window is None or not hasattr(main_window, "menuBar"):
        return False

    menu_bar = main_window.menuBar()
    menu = _find_or_create_menu(menu_bar, MENU_NAME)
    if menu is None:
        return False

    for action in menu.actions():
        if action.objectName() == COMMAND_NAME:
            _MENU_ACTION = action
            return True

    action = qt.QtGui.QAction(qt.QtGui.QIcon(icon_path()), "Open Sidebar", menu)
    action.setObjectName(COMMAND_NAME)
    action.setToolTip("Open the AI Agent Sidebar.")
    action.triggered.connect(open_sidebar)
    menu.addAction(action)
    _MENU_ACTION = action
    return True


def _find_or_create_menu(menu_bar, title: str):
    for action in menu_bar.actions():
        menu = action.menu()
        if menu is not None and _normalized_menu_title(menu.title()) == _normalized_menu_title(title):
            return menu
    return menu_bar.addMenu(title)


def _normalized_menu_title(title: str) -> str:
    return title.replace("&", "").strip()


register()
