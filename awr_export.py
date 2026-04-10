"""
awr_export.py

Exports all graph trace data from an AWR Design Environment project.

Reads measurement data directly via COM properties (XValue/YValue)
and writes tab-separated files from Python. This avoids ExportTraceData
which crashes AWR when called from external COM.
"""

import os
import re
import win32com.client
from tkinter import Tk, filedialog


def _sanitize_filename(name):
    """Replace characters illegal on Windows with underscores."""
    return re.sub(r'[/\\:*?"<>|]', '_', name.replace(" ", "_"))


def _connect_awr():
    """Connect to a running AWR instance."""
    for cls_name in ["AWR.MWOffice", "MWOApp.MWOffice", "MWOApp.MWOfficeApp"]:
        try:
            return win32com.client.Dispatch(cls_name)
        except Exception:
            continue
    return None


def _export_graph(graph, export_dir):
    """Read measurement data from a graph and write to a tab-separated file.

    Returns (filepath, n_measurements, n_points) on success, or None if
    the graph has no exportable data.
    """
    header_parts = []
    columns = []
    xvals = None
    n_points = None

    for mi in range(1, graph.Measurements.Count + 1):
        m = graph.Measurements.Item(mi)
        if not m.Enabled:
            continue
        try:
            npts = m.XPointCount
        except Exception:
            continue
        if npts == 0:
            continue

        try:
            if xvals is None:
                xvals_raw = [m.XValue(i) for i in range(1, npts + 1)]
                if xvals_raw[0] > 1e6:
                    xvals = [x / 1e9 for x in xvals_raw]
                    header_parts.append("Frequency (GHz)")
                else:
                    xvals = xvals_raw
                    header_parts.append("X")
                n_points = npts

            yvals = [m.YValue(i, 1) for i in range(1, min(npts, n_points) + 1)]
            header_parts.append(m.Name)
            columns.append(yvals)
        except Exception:
            continue

    if not columns:
        return None

    filename = _sanitize_filename(graph.Name) + ".txt"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w") as f:
        f.write("\t".join(header_parts) + "\n")
        for row in range(n_points):
            parts = [str(xvals[row])]
            for col in columns:
                parts.append(str(col[row]))
            f.write("\t".join(parts) + "\n")

    return filepath, len(columns), n_points


def export_all_graph_traces(project_path=None, export_dir=None):
    """Export all graph trace data from the currently open AWR project.

    The AWR project must already be open with simulations run.
    Measurements that are disabled or have no data are skipped.
    """
    if not export_dir:
        root = Tk()
        root.withdraw()
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        root.destroy()
        if not export_dir:
            print("No export directory selected.")
            return

    os.makedirs(export_dir, exist_ok=True)

    app = _connect_awr()
    if app is None:
        print("Failed to connect to AWR. Is it running?")
        return

    project = app.Project
    graph_count = project.Graphs.Count
    print(f"Connected to AWR — project: {project.Name} ({graph_count} graphs)")

    exported = 0
    skipped = 0

    for gi in range(1, graph_count + 1):
        graph = project.Graphs.Item(gi)
        result = _export_graph(graph, export_dir)

        if result is None:
            skipped += 1
            print(f"  SKIP (no data): {graph.Name}")
        else:
            filepath, n_meas, n_pts = result
            exported += 1
            print(f"  OK: {graph.Name} ({n_meas} measurements, {n_pts} points)")

    print(f"\nExport complete: {exported} exported, {skipped} skipped out of {graph_count} graphs.")
    print(f"Output: {export_dir}")


if __name__ == "__main__":
    export_all_graph_traces()
