# FreeCAD AI Agent Sidebar

FreeCAD AI Agent Sidebar is a FreeCAD 1.x addon that opens a dockable panel for sending compact FreeCAD document context to a local AI coding agent.

The MVP supports Codex CLI detection and asynchronous output streaming through Qt `QProcess`. Larger systems from the SRS, including local documentation retrieval, global skill installation, and automatic execution of generated FreeCAD Python code, are planned future slices.

## Development

Run the unit tests outside FreeCAD:

```bash
python -m unittest discover -s tests
```

Inside FreeCAD, install or symlink this repository as an addon, then load the `Open AI Agent Sidebar` command from the GUI environment.
