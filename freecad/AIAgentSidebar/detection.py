# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Detect supported local AI agent command line tools."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Callable


RunCommand = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class AgentInfo:
    name: str
    binary_path: str | None
    source: str | None
    available: bool
    diagnostic: str


class AgentDetector:
    """Detect AI agent CLIs with conservative, testable strategies."""

    CODEX_PACKAGE_NAMES = ("@openai/codex", "codex")
    CODEX_BINARY_NAMES = ("codex", "codex.cmd", "codex.exe")

    def __init__(
        self,
        which: Callable[[str], str | None] = shutil.which,
        run_command: RunCommand = subprocess.run,
    ) -> None:
        self._which = which
        self._run_command = run_command

    def detect_all(self) -> list[AgentInfo]:
        return [self.detect_codex()]

    def detect_codex(self) -> AgentInfo:
        binary_path = self._which("codex")
        if binary_path:
            return AgentInfo(
                name="codex",
                binary_path=binary_path,
                source="PATH",
                available=True,
                diagnostic="Codex CLI found on PATH.",
            )

        npm_result = self._detect_codex_from_npm()
        if npm_result is not None:
            return npm_result

        return AgentInfo(
            name="codex",
            binary_path=None,
            source=None,
            available=False,
            diagnostic="Codex CLI was not found on PATH or in global npm packages.",
        )

    def _detect_codex_from_npm(self) -> AgentInfo | None:
        package_list = self._run_npm(["ls", "-g", "--depth=0"])
        if package_list is None:
            return None

        installed = any(name in package_list.stdout for name in self.CODEX_PACKAGE_NAMES)
        if not installed:
            return None

        npm_root = self._run_npm(["root", "-g"])
        if npm_root is None:
            return AgentInfo(
                name="codex",
                binary_path=None,
                source="npm",
                available=False,
                diagnostic="Codex npm package is installed, but npm root could not be resolved.",
            )

        root = Path(npm_root.stdout.strip()).expanduser()
        binary_path = self._resolve_codex_binary_from_npm_root(root)
        if binary_path:
            return AgentInfo(
                name="codex",
                binary_path=str(binary_path),
                source="npm",
                available=True,
                diagnostic="Codex CLI found in global npm installation.",
            )

        return AgentInfo(
            name="codex",
            binary_path=None,
            source="npm",
            available=False,
            diagnostic="Codex npm package is installed, but no executable path was found.",
        )

    def _run_npm(self, args: list[str]) -> subprocess.CompletedProcess[str] | None:
        try:
            result = self._run_command(
                ["npm", *args],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (FileNotFoundError, subprocess.SubprocessError, OSError):
            return None

        if result.returncode != 0 and not result.stdout:
            return None
        return result

    def _resolve_codex_binary_from_npm_root(self, root: Path) -> Path | None:
        candidates: list[Path] = []

        if root.name == "node_modules":
            prefix = root.parent.parent if root.parent.name == "lib" else root.parent
            for binary_name in self.CODEX_BINARY_NAMES:
                candidates.append(prefix / "bin" / binary_name)

        package_root = root / "@openai" / "codex"
        candidates.extend(
            [
                package_root / "bin" / "codex.js",
                package_root / "dist" / "cli.js",
                package_root / "codex.js",
            ]
        )

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None
