# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

import unittest

from freecad.AIAgentSidebar import COMMAND_NAME
from freecad.AIAgentSidebar.init_gui import OpenAIAgentSidebarCommand, _normalized_menu_title


class InitGuiTests(unittest.TestCase):
    def test_command_exposes_icon_and_menu_text(self) -> None:
        resources = OpenAIAgentSidebarCommand().GetResources()

        self.assertEqual(resources["MenuText"], "Open AI Agent Sidebar")
        self.assertTrue(resources["Pixmap"].endswith("Logo.svg"))

    def test_menu_title_normalization_ignores_mnemonic_marker(self) -> None:
        self.assertEqual(_normalized_menu_title("&AI Agent"), "AI Agent")

    def test_command_name_is_stable_for_menu_action(self) -> None:
        self.assertEqual(COMMAND_NAME, "AIAgentSidebar_Open")


if __name__ == "__main__":
    unittest.main()
