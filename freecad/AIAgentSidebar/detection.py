# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Detect supported local AI agent command line tools."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import Callable, Iterable


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
        extra_search_paths: Iterable[str | Path] | None = None,
        use_login_shell: bool = True,
    ) -> None:
        self._which = which
        self._run_command = run_command
        self._extra_search_paths = tuple(extra_search_paths) if extra_search_paths is not None else self._default_search_paths()
        self._use_login_shell = use_login_shell

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

        binary_path = self._find_executable_in_paths("codex")
        if binary_path:
            return AgentInfo(
                name="codex",
                binary_path=str(binary_path),
                source="common path",
                available=True,
                diagnostic="Codex CLI found in a common user tool directory.",
            )

        binary_path = self._find_executable_from_login_shell("codex")
        if binary_path:
            return AgentInfo(
                name="codex",
                binary_path=binary_path,
                source="login shell",
                available=True,
                diagnostic="Codex CLI found from the user's login shell PATH.",
            )

        npm_result = self._detect_codex_from_npm()
        if npm_result is not None:
            return npm_result

        return AgentInfo(
            name="codex",
            binary_path=None,
            source=None,
            available=False,
            diagnostic="Codex CLI was not found on PATH, common tool paths, login shell PATH, or global npm packages.",
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
        npm = self._which("npm") or str(self._find_executable_in_paths("npm") or "")
        if not npm:
            npm = self._find_executable_from_login_shell("npm") or "npm"

        try:
            result = self._run_command(
                [npm, *args],
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

    def _find_executable_in_paths(self, executable_name: str) -> Path | None:
        for directory in self._extra_search_paths:
            candidate = Path(directory).expanduser() / executable_name
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None

    def _find_executable_from_login_shell(self, executable_name: str) -> str | None:
        if not self._use_login_shell:
            return None

        shell = os.environ.get("SHELL")
        if not shell or not Path(shell).exists():
            shell = "/bin/zsh" if Path("/bin/zsh").exists() else "/bin/sh"

        try:
            result = self._run_command(
                [shell, "-lc", f"command -v {executable_name}"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (FileNotFoundError, subprocess.SubprocessError, OSError):
            return None

        if result.returncode != 0:
            return None

        path = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        if not path:
            return None
        return path

    def _default_search_paths(self) -> tuple[Path, ...]:
        home = Path.home()
        return (
            Path("/opt/homebrew/bin"),
            Path("/usr/local/bin"),
            Path("/opt/local/bin"),
            home / ".local" / "bin",
            home / ".npm-global" / "bin",
            home / ".bun" / "bin",
            home / ".cargo" / "bin",
        )

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
