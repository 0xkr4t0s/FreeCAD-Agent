# FreeCAD AI Agent Sidebar Workspace Instructions

This repository builds a FreeCAD 1.x addon that exposes a dockable AI agent sidebar.

## Engineering Notes

- Prefer FreeCAD 1.x and PySide6 APIs, with small compatibility shims when they keep tests importable outside FreeCAD.
- Keep addon entrypoints compatible with FreeCAD loading conventions: top-level `InitGui.py` and package code under `freecad/AIAgentSidebar/`.
- Keep CLI-agent integrations mockable. Do not require Codex, npm, FreeCAD, or PySide to be installed for unit tests.
- Do not add third-party runtime dependencies without an explicit project decision.
- Keep generated FreeCAD context compact. The full local documentation retrieval and macro execution loop are future slices.
