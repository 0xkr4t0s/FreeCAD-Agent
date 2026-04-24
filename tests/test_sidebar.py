# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

import unittest

from freecad.AIAgentSidebar.sidebar import CODEX_EXEC_ARGS


class SidebarTests(unittest.TestCase):
    def test_codex_exec_args_use_non_interactive_stdin_mode(self) -> None:
        self.assertEqual(CODEX_EXEC_ARGS[0], "exec")
        self.assertIn("--skip-git-repo-check", CODEX_EXEC_ARGS)
        self.assertIn("--color", CODEX_EXEC_ARGS)
        self.assertEqual(CODEX_EXEC_ARGS[-1], "-")


if __name__ == "__main__":
    unittest.main()
