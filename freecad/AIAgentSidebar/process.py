# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Asynchronous process bridge for AI agent CLIs."""

from __future__ import annotations

from typing import Any, Callable

from .qt_compat import QtUnavailableError, load_qt, signal_type
from .signals import SimpleSignal


try:
    _QT = load_qt()
    _QT_CORE = _QT.QtCore
    _SIGNAL = signal_type(_QT_CORE)
except QtUnavailableError:
    _QT = None
    _QT_CORE = None
    _SIGNAL = None


if _QT_CORE is not None and _SIGNAL is not None:

    class AgentProcess(_QT_CORE.QObject):  # type: ignore[misc]
        """QProcess wrapper that exposes streamed output as signals."""

        output_received = _SIGNAL(str)
        error_received = _SIGNAL(str)
        started = _SIGNAL()
        finished = _SIGNAL(int, int)
        failed = _SIGNAL(str)

        def __init__(self, process_factory: Callable[[], Any] | None = None) -> None:
            super().__init__()
            self._process_factory = process_factory or (lambda: _QT_CORE.QProcess(self))
            self._process: Any | None = None

        def start(
            self,
            binary_path: str,
            args: list[str] | None = None,
            working_dir: str | None = None,
        ) -> None:
            self._process = self._process_factory()
            if working_dir and hasattr(self._process, "setWorkingDirectory"):
                self._process.setWorkingDirectory(working_dir)

            self._connect_process_signals()
            self._process.start(binary_path, args or [])

        def send(self, text: str) -> None:
            if self._process is None:
                self.failed.emit("Agent process is not running.")
                return
            payload = text if text.endswith("\n") else f"{text}\n"
            self._process.write(payload.encode("utf-8"))

        def stop(self) -> None:
            if self._process is None:
                return
            self._process.terminate()

        def _connect_process_signals(self) -> None:
            process = self._process
            process.readyReadStandardOutput.connect(self._read_stdout)
            process.readyReadStandardError.connect(self._read_stderr)
            process.started.connect(self.started.emit)
            process.finished.connect(self.finished.emit)

            error_signal = getattr(process, "errorOccurred", None)
            if error_signal is not None:
                error_signal.connect(lambda error: self.failed.emit(str(error)))

        def _read_stdout(self) -> None:
            if self._process is not None:
                self.output_received.emit(_decode_qbytearray(self._process.readAllStandardOutput()))

        def _read_stderr(self) -> None:
            if self._process is not None:
                self.error_received.emit(_decode_qbytearray(self._process.readAllStandardError()))

else:

    class AgentProcess:
        """Headless fallback with the same public API for tests."""

        def __init__(self, process_factory: Callable[[], Any] | None = None) -> None:
            self.output_received = SimpleSignal()
            self.error_received = SimpleSignal()
            self.started = SimpleSignal()
            self.finished = SimpleSignal()
            self.failed = SimpleSignal()
            self._process_factory = process_factory
            self._process: Any | None = None

        def start(
            self,
            binary_path: str,
            args: list[str] | None = None,
            working_dir: str | None = None,
        ) -> None:
            if self._process_factory is None:
                self.failed.emit("Qt is unavailable and no process factory was provided.")
                return
            self._process = self._process_factory()
            if working_dir and hasattr(self._process, "setWorkingDirectory"):
                self._process.setWorkingDirectory(working_dir)
            self._connect_process_signals()
            self._process.start(binary_path, args or [])

        def send(self, text: str) -> None:
            if self._process is None:
                self.failed.emit("Agent process is not running.")
                return
            payload = text if text.endswith("\n") else f"{text}\n"
            self._process.write(payload.encode("utf-8"))

        def stop(self) -> None:
            if self._process is not None:
                self._process.terminate()

        def _connect_process_signals(self) -> None:
            process = self._process
            process.readyReadStandardOutput.connect(self._read_stdout)
            process.readyReadStandardError.connect(self._read_stderr)
            process.started.connect(self.started.emit)
            process.finished.connect(self.finished.emit)
            if hasattr(process, "errorOccurred"):
                process.errorOccurred.connect(lambda error: self.failed.emit(str(error)))

        def _read_stdout(self) -> None:
            if self._process is not None:
                self.output_received.emit(_decode_qbytearray(self._process.readAllStandardOutput()))

        def _read_stderr(self) -> None:
            if self._process is not None:
                self.error_received.emit(_decode_qbytearray(self._process.readAllStandardError()))


def _decode_qbytearray(data: Any) -> str:
    if isinstance(data, bytes):
        raw = data
    else:
        raw = bytes(data)
    return raw.decode("utf-8", errors="replace")
