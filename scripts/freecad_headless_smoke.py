# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Headless smoke test for FreeCADCmd.

Run with:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd scripts/freecad_headless_smoke.py
"""

from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    import FreeCAD  # type: ignore
    import freecad  # type: ignore

    addon_namespace = str(REPO_ROOT / "freecad")
    if addon_namespace not in freecad.__path__:
        freecad.__path__.insert(0, addon_namespace)

    from freecad.AIAgentSidebar.context import FreeCADContextProvider
    from freecad.AIAgentSidebar.detection import AgentDetector
    from freecad.AIAgentSidebar.prompt import PromptBuilder

    ET.parse(REPO_ROOT / "package.xml")

    document = FreeCAD.newDocument("AIAgentSidebarSmoke")
    try:
        box = document.addObject("Part::Box", "SmokeBox")
        document.recompute()

        snapshot = FreeCADContextProvider(FreeCAD, None).snapshot()
        prompt = PromptBuilder().build("Describe the current document.", snapshot)
        codex = AgentDetector().detect_codex()

        assert snapshot.document_name == "AIAgentSidebarSmoke", snapshot
        assert "Active document: AIAgentSidebarSmoke" in prompt, prompt
        assert box.Name == "SmokeBox"
        assert codex.name == "codex"

        print("FreeCAD headless smoke OK")
        print(f"FreeCAD version: {'.'.join(FreeCAD.Version()[:3])}")
        print(f"Codex available: {codex.available}")
        return 0
    finally:
        FreeCAD.closeDocument(document.Name)


if __name__ == "__main__":
    raise SystemExit(main())
