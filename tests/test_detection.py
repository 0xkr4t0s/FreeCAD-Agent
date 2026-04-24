# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

from pathlib import Path
import subprocess
import tempfile
import unittest

from freecad.AIAgentSidebar.detection import AgentDetector


class AgentDetectorTests(unittest.TestCase):
    def test_detects_codex_on_path(self) -> None:
        detector = AgentDetector(which=lambda name: "/usr/local/bin/codex", use_login_shell=False)

        info = detector.detect_codex()

        self.assertTrue(info.available)
        self.assertEqual(info.binary_path, "/usr/local/bin/codex")
        self.assertEqual(info.source, "PATH")

    def test_returns_unavailable_when_codex_is_missing(self) -> None:
        detector = AgentDetector(
            which=lambda name: None,
            run_command=self._npm_missing,
            extra_search_paths=(),
            use_login_shell=False,
        )

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

            detector = AgentDetector(
                which=lambda name: None,
                run_command=run_command,
                extra_search_paths=(),
                use_login_shell=False,
            )

            info = detector.detect_codex()

            self.assertTrue(info.available)
            self.assertEqual(info.binary_path, str(executable))
            self.assertEqual(info.source, "npm")

    def test_detects_codex_from_common_tool_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "codex"
            executable.write_text("#!/usr/bin/env node\n", encoding="utf-8")
            executable.chmod(0o755)

            detector = AgentDetector(
                which=lambda name: None,
                run_command=self._npm_missing,
                extra_search_paths=(temp_dir,),
                use_login_shell=False,
            )

            info = detector.detect_codex()

            self.assertTrue(info.available)
            self.assertEqual(info.binary_path, str(executable))
            self.assertEqual(info.source, "common path")

    def test_detects_codex_from_login_shell(self) -> None:
        def run_command(command, **kwargs):
            if command[-1] == "command -v codex":
                return subprocess.CompletedProcess(command, 0, stdout="/opt/homebrew/bin/codex\n", stderr="")
            return self._npm_missing(command, **kwargs)

        detector = AgentDetector(
            which=lambda name: None,
            run_command=run_command,
            extra_search_paths=(),
            use_login_shell=True,
        )

        info = detector.detect_codex()

        self.assertTrue(info.available)
        self.assertEqual(info.binary_path, "/opt/homebrew/bin/codex")
        self.assertEqual(info.source, "login shell")

    def _npm_missing(self, command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


if __name__ == "__main__":
    unittest.main()
