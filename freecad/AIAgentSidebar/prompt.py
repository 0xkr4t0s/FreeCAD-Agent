# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

"""Prompt construction helpers."""

from __future__ import annotations

from .context import ContextSnapshot


class PromptBuilder:
    """Prefix user prompts with compact FreeCAD state."""

    def build(self, user_prompt: str, context: ContextSnapshot) -> str:
        lines = ["FreeCAD context:"]

        if context.document_name:
            lines.append(f"- Active document: {context.document_name}")
        else:
            lines.append("- Active document: none")

        if context.selected_objects:
            lines.append("- Selection:")
            for selected in context.selected_objects:
                label = f" label={selected.label!r}" if selected.label else ""
                type_id = f" type={selected.type_id}" if selected.type_id else ""
                lines.append(f"  - name={selected.name!r}{label}{type_id}")
        else:
            lines.append("- Selection: none")

        if context.diagnostic:
            lines.append(f"- Context diagnostic: {context.diagnostic}")

        lines.append("")
        lines.append("User request:")
        lines.append(user_prompt.rstrip())
        return "\n".join(lines)
