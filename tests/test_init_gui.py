# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

import unittest
from unittest.mock import patch

from freecad.AIAgentSidebar import COMMAND_NAME
import freecad.AIAgentSidebar.init_gui as init_gui
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

    def test_menu_install_retries_are_scheduled_once(self) -> None:
        fake_qt = FakeQt()
        FakeTimer.calls = []
        init_gui._MENU_INSTALL_SCHEDULED = False

        with patch.object(init_gui, "load_qt", return_value=fake_qt):
            init_gui.schedule_menu_action_install(object())
            init_gui.schedule_menu_action_install(object())

        self.assertEqual([delay for delay, _callback in fake_qt.QtCore.QTimer.calls], [0, 250, 1000, 3000])
        init_gui._MENU_INSTALL_SCHEDULED = False


class FakeQt:
    def __init__(self) -> None:
        self.QtCore = type("QtCore", (), {"QTimer": FakeTimer})


class FakeTimer:
    calls = []

    @classmethod
    def singleShot(cls, delay_ms, callback):  # noqa: N802 - Qt API naming
        cls.calls.append((delay_ms, callback))


if __name__ == "__main__":
    unittest.main()
