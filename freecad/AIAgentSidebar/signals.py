# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Fallback signal primitive for tests and headless imports."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class SimpleSignal:
    """Tiny connect/emit signal used when Qt is unavailable."""

    def __init__(self) -> None:
        self._slots: list[Callable[..., Any]] = []

    def connect(self, slot: Callable[..., Any]) -> None:
        self._slots.append(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self._slots):
            slot(*args)
