# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

from pathlib import Path
import subprocess
import tempfile
import unittest

from freecad.AIAgentSidebar.detection import AgentDetector


class AgentDetectorTests(unittest.TestCase):
    def test_detects_codex_on_path(self) -> None:
        detector = AgentDetector(which=lambda name: "/usr/local/bin/codex")

        info = detector.detect_codex()

        self.assertTrue(info.available)
        self.assertEqual(info.binary_path, "/usr/local/bin/codex")
        self.assertEqual(info.source, "PATH")

    def test_returns_unavailable_when_codex_is_missing(self) -> None:
        detector = AgentDetector(which=lambda name: None, run_command=self._npm_missing)

        info = detector.detect_codex()

        self.assertFalse(info.available)
        self.assertIsNone(info.binary_path)
        self.assertIn("not found", info.diagnostic)

    def test_detects_codex_from_global_npm_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package_bin = root / "@openai" / "codex" / "bin"
            package_bin.mkdir(parents=True, exist_ok=True)
            executable = package_bin / "codex.js"
            executable.write_text("#!/usr/bin/env node\n", encoding="utf-8")

            def run_command(command, **kwargs):
                if command == ["npm", "ls", "-g", "--depth=0"]:
                    return subprocess.CompletedProcess(command, 0, stdout="`-- @openai/codex@1.0.0\n", stderr="")
                if command == ["npm", "root", "-g"]:
                    return subprocess.CompletedProcess(command, 0, stdout=f"{root}\n", stderr="")
                raise AssertionError(command)

            detector = AgentDetector(which=lambda name: None, run_command=run_command)

            info = detector.detect_codex()

            self.assertTrue(info.available)
            self.assertEqual(info.binary_path, str(executable))
            self.assertEqual(info.source, "npm")

    def _npm_missing(self, command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


if __name__ == "__main__":
    unittest.main()
