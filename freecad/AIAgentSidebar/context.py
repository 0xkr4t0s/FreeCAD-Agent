# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Read compact FreeCAD state for prompt injection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SelectedObject:
    name: str
    label: str | None = None
    type_id: str | None = None


@dataclass(frozen=True)
class ContextSnapshot:
    document_name: str | None = None
    selected_objects: list[SelectedObject] = field(default_factory=list)
    diagnostic: str | None = None


class FreeCADContextProvider:
    """Collect the small amount of state needed by the MVP prompt builder."""

    def __init__(self, freecad_module: Any | None = None, freecad_gui_module: Any | None = None) -> None:
        self._freecad = freecad_module
        self._freecad_gui = freecad_gui_module

    def snapshot(self) -> ContextSnapshot:
        try:
            freecad = self._freecad or __import__("FreeCAD")
            freecad_gui = self._freecad_gui or __import__("FreeCADGui")
        except ImportError:
            return ContextSnapshot(diagnostic="FreeCAD modules are unavailable outside FreeCAD.")

        document_name = self._document_name(freecad)
        selected_objects = self._selected_objects(freecad_gui)
        return ContextSnapshot(document_name=document_name, selected_objects=selected_objects)

    def _document_name(self, freecad: Any) -> str | None:
        document = getattr(freecad, "ActiveDocument", None)
        if document is None:
            return None
        return getattr(document, "Name", None) or getattr(document, "Label", None)

    def _selected_objects(self, freecad_gui: Any) -> list[SelectedObject]:
        selection = getattr(freecad_gui, "Selection", None)
        if selection is None or not hasattr(selection, "getSelection"):
            return []

        try:
            objects = selection.getSelection()
        except Exception as exc:
            return [SelectedObject(name="<selection unavailable>", label=str(exc))]

        selected: list[SelectedObject] = []
        for obj in objects:
            name = str(getattr(obj, "Name", "<unnamed>"))
            label = getattr(obj, "Label", None)
            type_id = getattr(obj, "TypeId", None)
            selected.append(SelectedObject(name=name, label=label, type_id=type_id))
        return selected
