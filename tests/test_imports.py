# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

import importlib
import unittest


class ImportSmokeTests(unittest.TestCase):
    def test_core_modules_import_outside_freecad(self) -> None:
        modules = [
            "freecad.AIAgentSidebar",
            "freecad.AIAgentSidebar.context",
            "freecad.AIAgentSidebar.detection",
            "freecad.AIAgentSidebar.prompt",
            "freecad.AIAgentSidebar.process",
            "freecad.AIAgentSidebar.resources",
            "freecad.AIAgentSidebar.sidebar",
            "freecad.AIAgentSidebar.init_gui",
        ]

        for module in modules:
            with self.subTest(module=module):
                importlib.import_module(module)


if __name__ == "__main__":
    unittest.main()
