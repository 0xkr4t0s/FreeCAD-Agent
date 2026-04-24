<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon. -->

# MVP Usage

Open the AI Agent Sidebar command from FreeCAD after installing the addon. The sidebar detects `codex` on `PATH` first and then checks global npm packages.

When you send a prompt, the addon prepends compact FreeCAD state containing the active document and selected object names. The prompt is written to the Codex process and stdout/stderr are streamed into the sidebar transcript.
