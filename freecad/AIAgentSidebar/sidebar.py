# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Dockable sidebar UI for FreeCAD."""

from __future__ import annotations

from . import DOCK_OBJECT_NAME
from .context import FreeCADContextProvider
from .detection import AgentDetector, AgentInfo
from .process import AgentProcess
from .prompt import PromptBuilder
from .qt_compat import QtUnavailableError, load_qt


_DOCK = None
CODEX_EXEC_ARGS = ["exec", "--skip-git-repo-check", "--color", "never", "-"]

try:
    _QT = load_qt()
    _WIDGET_BASE = _QT.QtWidgets.QWidget
except QtUnavailableError:
    _QT = None
    _WIDGET_BASE = object


def open_sidebar() -> object:
    """Create or focus the singleton sidebar dock."""

    global _DOCK

    qt = load_qt()
    try:
        import FreeCADGui  # type: ignore
    except ImportError as exc:
        raise RuntimeError("AI Agent Sidebar can only be opened inside FreeCAD.") from exc

    main_window = FreeCADGui.getMainWindow()
    if _DOCK is not None:
        _DOCK.show()
        _DOCK.raise_()
        return _DOCK

    dock = qt.QtWidgets.QDockWidget("AI Agent Sidebar", main_window)
    dock.setObjectName(DOCK_OBJECT_NAME)
    dock.setAllowedAreas(qt.QtCore.Qt.LeftDockWidgetArea | qt.QtCore.Qt.RightDockWidgetArea)
    dock.setWidget(AIAgentSidebarWidget())
    main_window.addDockWidget(qt.QtCore.Qt.RightDockWidgetArea, dock)
    _DOCK = dock
    return dock


class AIAgentSidebarWidget(_WIDGET_BASE):
    """Main sidebar widget."""

    def __init__(
        self,
        detector: AgentDetector | None = None,
        process: AgentProcess | None = None,
        context_provider: FreeCADContextProvider | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        if _QT is None:
            raise RuntimeError("Qt bindings are unavailable; the sidebar can only be created inside FreeCAD.")
        if getattr(self, "_initialized", False):
            return

        super().__init__()
        self._qt = _QT
        self._detector = detector or AgentDetector()
        self._process = process or AgentProcess()
        self._context_provider = context_provider or FreeCADContextProvider()
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._agent_info: AgentInfo = self._detector.detect_codex()
        self._running = False

        self._build_ui()
        self._connect_signals()
        self._refresh_agent_status()
        self._initialized = True

    def _build_ui(self) -> None:
        widgets = self._qt.QtWidgets

        layout = widgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.status_label = widgets.QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.transcript = widgets.QPlainTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setPlaceholderText("Agent output appears here.")
        layout.addWidget(self.transcript, 1)

        self.prompt_input = widgets.QPlainTextEdit()
        self.prompt_input.setPlaceholderText("Describe the FreeCAD task.")
        self.prompt_input.setMaximumHeight(110)
        layout.addWidget(self.prompt_input)

        row = widgets.QHBoxLayout()
        self.run_button = widgets.QPushButton("Run")
        self.stop_button = widgets.QPushButton("Stop")
        self.refresh_button = widgets.QPushButton("Refresh Agent")
        row.addWidget(self.run_button)
        row.addWidget(self.stop_button)
        row.addWidget(self.refresh_button)
        layout.addLayout(row)

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(self._run_prompt)
        self.stop_button.clicked.connect(self._process.stop)
        self.refresh_button.clicked.connect(self._refresh_detection)
        self._process.output_received.connect(lambda text: self._append(text))
        self._process.error_received.connect(lambda text: self._append(text, prefix="[stderr] "))
        self._process.started.connect(lambda: self._append("Agent process started.\n"))
        self._process.failed.connect(lambda text: self._append(f"[error] {text}\n"))
        self._process.finished.connect(self._on_process_finished)

    def _refresh_detection(self) -> None:
        self._agent_info = self._detector.detect_codex()
        self._refresh_agent_status()

    def _refresh_agent_status(self) -> None:
        if self._agent_info.available:
            self.status_label.setText(f"Codex: {self._agent_info.binary_path}")
            self.run_button.setEnabled(True)
        else:
            self.status_label.setText(f"Codex unavailable: {self._agent_info.diagnostic}")
            self.run_button.setEnabled(False)

    def _run_prompt(self) -> None:
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return
        if not self._agent_info.available or not self._agent_info.binary_path:
            self._append("[error] Codex CLI is unavailable.\n")
            return

        built_prompt = self._prompt_builder.build(prompt, self._context_provider.snapshot())
        self._append(f"> {prompt}\n\n")
        if self._running:
            self._append("[error] Agent process is already running. Stop it or wait for it to finish.\n")
            return

        self._running = True
        self._process.start(self._agent_info.binary_path, list(CODEX_EXEC_ARGS), None)
        self._process.send(built_prompt)
        self._process.close_input()

    def _on_process_finished(self, code: int, status: int) -> None:
        self._running = False
        self._append(f"Agent process finished: {code} ({status}).\n")

    def _append(self, text: str, prefix: str = "") -> None:
        self.transcript.moveCursor(self._qt.QtGui.QTextCursor.End)
        self.transcript.insertPlainText(prefix + text)
        self.transcript.moveCursor(self._qt.QtGui.QTextCursor.End)
