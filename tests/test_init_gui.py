# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

import unittest

from freecad.AIAgentSidebar import COMMAND_NAME
from freecad.AIAgentSidebar.init_gui import AIAgentSidebarWorkbench, OpenAIAgentSidebarCommand


class InitGuiTests(unittest.TestCase):
    def test_command_exposes_icon_and_menu_text(self) -> None:
        resources = OpenAIAgentSidebarCommand().GetResources()

        self.assertEqual(resources["MenuText"], "Open AI Agent Sidebar")
        self.assertTrue(resources["Pixmap"].endswith("Logo.svg"))

    def test_workbench_adds_toolbar_and_menu(self) -> None:
        workbench = RecordingWorkbench()

        AIAgentSidebarWorkbench.Initialize(workbench)

        self.assertEqual(workbench.toolbars, [("AI Agent Sidebar", [COMMAND_NAME])])
        self.assertEqual(workbench.menus, [("AI Agent Sidebar", [COMMAND_NAME])])
        self.assertEqual(AIAgentSidebarWorkbench().GetClassName(), "Gui::PythonWorkbench")


class RecordingWorkbench:
    def __init__(self) -> None:
        self.toolbars = []
        self.menus = []

    def appendToolbar(self, name, commands):  # noqa: N802 - FreeCAD API naming
        self.toolbars.append((name, commands))

    def appendMenu(self, name, commands):  # noqa: N802 - FreeCAD API naming
        self.menus.append((name, commands))


if __name__ == "__main__":
    unittest.main()
