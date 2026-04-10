"""
awr_export.py

Exports all graph trace data from an AWR Design Environment project.

Strategy: ExportTraceData crashes AWR when called via external COM or
Routine.Run(). The stable path is running a .bas script from AWR's
internal Script Editor (F5). This module:
  1. Generates a .bas export script with the output directory baked in.
  2. Imports it into AWR's GlobalScripts via one lightweight COM call.
  3. Prompts the user to press F5 in AWR's Script Editor.
  4. Waits for the export files to appear, then reports results.
"""

import os
import re
import time
import win32com.client
from tkinter import Tk, filedialog


_BAS_TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "scripts", "export_all_graphs.bas")

SCRIPT_NAME = "export_all_graphs"


def _connect_awr():
    """Connect to a running AWR instance."""
    com_classes = [
        "AWR.MWOffice",
        "MWOApp.MWOffice",
        "MWOApp.MWOfficeApp",
    ]
    for cls_name in com_classes:
        try:
            return win32com.client.Dispatch(cls_name)
        except Exception:
            continue
    return None


def _generate_bas(export_dir):
    """Generate a .bas script with the export directory baked in."""
    export_dir = export_dir.replace("/", "\\")
    if not export_dir.endswith("\\"):
        export_dir += "\\"
    with open(_BAS_TEMPLATE_FILE, "r") as f:
        template = f.read()
    # Replace the hardcoded output directory in the template
    return re.sub(
        r'exportDir = ".*?"',
        f'exportDir = "{export_dir}"',
        template,
    )


def export_all_graph_traces(project_path=None, export_dir=None):
    """Export all graph trace data from the currently open AWR project.

    The AWR project must already be open with simulations run.
    If project_path is given it is ignored (kept for CLI compatibility).
    """
    # Prompt for export directory if not provided
    if not export_dir:
        root = Tk()
        root.withdraw()
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        root.destroy()
        if not export_dir:
            print("No export directory selected.")
            return

    os.makedirs(export_dir, exist_ok=True)

    # Connect to running AWR
    app = _connect_awr()
    if app is None:
        print("Failed to connect to AWR. Is it running?")
        return

    project_name = app.Project.Name
    graph_count = app.Project.Graphs.Count
    print(f"Connected to AWR — project: {project_name} ({graph_count} graphs)")

    # Write .bas script to disk
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    bas_path = os.path.join(scripts_dir, f"{SCRIPT_NAME}.bas")

    with open(bas_path, "w") as f:
        f.write(_generate_bas(export_dir))
    print(f"Generated script: {bas_path}")

    # Import into AWR GlobalScripts
    if app.GlobalScripts.Exists(SCRIPT_NAME):
        app.GlobalScripts.Remove(SCRIPT_NAME)
    app.GlobalScripts.Import(bas_path)
    print(f"Script '{SCRIPT_NAME}' loaded into AWR GlobalScripts.")

    print()
    print("=" * 60)
    print("  NEXT STEP — run the script inside AWR:")
    print()
    print("  1. In AWR: View > Script Editor  (or Alt+F11)")
    print(f"  2. Open '{SCRIPT_NAME}' under Global Scripts")
    print("  3. Press F5 to run")
    print("  4. Check the Debug window for progress")
    print("=" * 60)
    print()

    # Wait for user to run the script, then report results
    input("Press Enter here after the AWR script finishes...")

    # Report what was exported
    exported = [f for f in os.listdir(export_dir) if f.endswith(".txt")]
    print(f"\nExport complete: {len(exported)} files in {export_dir}")
    for f in sorted(exported):
        size = os.path.getsize(os.path.join(export_dir, f))
        print(f"  {f}  ({size:,} bytes)")


if __name__ == "__main__":
    export_all_graph_traces()
