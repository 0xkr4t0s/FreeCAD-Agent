# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Small Qt compatibility helpers.

FreeCAD 1.x normally embeds PySide6. The fallback keeps the code importable in
older FreeCAD builds and lets non-UI unit tests run without Qt installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any


class QtUnavailableError(ImportError):
    """Raised when neither supported PySide binding can be imported."""


@dataclass(frozen=True)
class QtBinding:
    name: str
    QtCore: Any
    QtGui: Any
    QtWidgets: Any


def load_qt() -> QtBinding:
    """Load PySide6 first, then PySide2."""

    errors: list[str] = []
    for binding_name in ("PySide6", "PySide2"):
        try:
            return QtBinding(
                name=binding_name,
                QtCore=import_module(f"{binding_name}.QtCore"),
                QtGui=import_module(f"{binding_name}.QtGui"),
                QtWidgets=import_module(f"{binding_name}.QtWidgets"),
            )
        except ImportError as exc:
            errors.append(f"{binding_name}: {exc}")
    raise QtUnavailableError("Qt bindings unavailable: " + "; ".join(errors))


def signal_type(qt_core: Any) -> Any:
    """Return the signal constructor for PySide6 or PySide2."""

    return getattr(qt_core, "Signal", getattr(qt_core, "pyqtSignal", None))
