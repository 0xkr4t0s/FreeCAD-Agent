# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

from types import SimpleNamespace
import unittest

from freecad.AIAgentSidebar.context import FreeCADContextProvider
from freecad.AIAgentSidebar.prompt import PromptBuilder


class PromptContextTests(unittest.TestCase):
    def test_snapshot_reads_document_and_selection_names(self) -> None:
        freecad = SimpleNamespace(ActiveDocument=SimpleNamespace(Name="Assembly"))
        selected = [
            SimpleNamespace(Name="Pad001", Label="Main Pad", TypeId="PartDesign::Pad"),
            SimpleNamespace(Name="Sketch002", Label="Profile", TypeId="Sketcher::SketchObject"),
        ]
        freecad_gui = SimpleNamespace(Selection=SimpleNamespace(getSelection=lambda: selected))

        snapshot = FreeCADContextProvider(freecad, freecad_gui).snapshot()

        self.assertEqual(snapshot.document_name, "Assembly")
        self.assertEqual([item.name for item in snapshot.selected_objects], ["Pad001", "Sketch002"])

    def test_prompt_builder_includes_empty_state_and_user_prompt(self) -> None:
        snapshot = FreeCADContextProvider(
            SimpleNamespace(ActiveDocument=None),
            SimpleNamespace(Selection=SimpleNamespace(getSelection=lambda: [])),
        ).snapshot()

        prompt = PromptBuilder().build("Create a 10 mm cube.", snapshot)

        self.assertIn("Active document: none", prompt)
        self.assertIn("Selection: none", prompt)
        self.assertTrue(prompt.endswith("Create a 10 mm cube."))


if __name__ == "__main__":
    unittest.main()
