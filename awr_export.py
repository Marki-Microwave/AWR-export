"""
awr_export.py

Exports all graph trace data from an AWR Design Environment project.

Reads measurement data directly via COM properties (XValue/YValue)
and writes tab-separated files from Python. This avoids ExportTraceData
which crashes AWR when called from external COM.
"""

import os
import re
from collections import namedtuple

import win32com.client
from tkinter import Tk, filedialog

# Constants from the AWR API enums mwUnitType / mwUnitMultType.
MW_UT_FREQUENCY = 1
MW_UT_TEMPERATURE = 8
MW_UT_CURRENT = 12
MW_UT_POWER_LOG = 13
MW_UT_POWER = 14
MW_UT_DB = 15
MW_UT_DB_ONLY_POWER = 18
MW_UMT_DEGC = 15
MW_UMT_DEGK = 16
MW_UMT_DEGF = 17
MW_UMT_DBM = 20
MW_UMT_DBW = 21

_Unit = namedtuple("_Unit", ["type", "mult_type", "mult_value", "unit_string"])


def _build_unit_table(com_units):
    """Snapshot the project's Units collection into {unit_type: _Unit}.

    Keyed by mwUnitType so entries can be looked up from
    Measurement.UnitType(axis) regardless of collection ordering.
    """
    table = {}
    for i in range(1, com_units.Count + 1):
        try:
            u = com_units.Item(i)
            table[u.Type] = _Unit(u.Type, u.MultType, u.MultValue, u.UnitString)
        except Exception:
            continue
    return table


def _to_display(value, unit):
    """Convert a raw base-unit value to the project's display unit.

    XValue/YValue return base units (Hz, W, V, dBW, Kelvin...) while graphs
    display per the project Units table. Log-power and temperature are the
    only non-multiplicative unit types; everything else scales by MultValue.
    """
    if unit is None:
        return value
    if unit.type in (MW_UT_POWER_LOG, MW_UT_DB_ONLY_POWER):
        # base is dB re 1 W (dBW)
        return value + 30.0 if unit.mult_type == MW_UMT_DBM else value
    if unit.type == MW_UT_TEMPERATURE:
        # base is Kelvin
        if unit.mult_type == MW_UMT_DEGC:
            return value - 273.15
        if unit.mult_type == MW_UMT_DEGF:
            return value * 1.8 - 459.67
        return value
    if unit.mult_value:
        return value / unit.mult_value
    return value


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


def _axis_unit(m, axis_index, units):
    """Look up the display unit for a measurement axis (1 = x, 2 = y)."""
    try:
        return units.get(m.UnitType(axis_index))
    except Exception:
        return None


def _export_graph(graph, export_dir, units):
    """Read measurement data from a graph and write to a tab-separated file.

    Values are converted from COM base units to the project's display units
    (the units shown on the graph). Measurements sharing an x-vector share
    one x column; measurements on a different x grid (e.g. measured file
    data overlaid on a simulated sweep) get their own x column, with short
    columns padded by empty cells. Returns (filepath, n_measurements,
    n_rows) on success, or None if the graph has no exportable data.
    """
    # each group: [xheader, xvals, [meas headers], [y columns]]
    groups = []

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
            xvals_raw = [m.XValue(i) for i in range(1, npts + 1)]
            xunit = _axis_unit(m, 1, units)
            if xunit is not None:
                xvals = [_to_display(x, xunit) for x in xvals_raw]
                if xunit.type == MW_UT_FREQUENCY:
                    xheader = f"Frequency ({xunit.unit_string})"
                else:
                    xheader = "X"
            elif xvals_raw[0] > 1e6:
                # unit lookup unavailable — fall back to Hz->GHz heuristic
                xvals = [x / 1e9 for x in xvals_raw]
                xheader = "Frequency (GHz)"
            else:
                xvals = xvals_raw
                xheader = "X"

            yunit = _axis_unit(m, 2, units)
            yvals = [_to_display(m.YValue(i, 1), yunit)
                     for i in range(1, npts + 1)]
        except Exception:
            continue

        for grp in groups:
            if grp[1] == xvals:
                grp[2].append(m.Name)
                grp[3].append(yvals)
                break
        else:
            groups.append([xheader, xvals, [m.Name], [yvals]])

    if not groups:
        return None

    filename = _sanitize_filename(graph.Name) + ".txt"
    filepath = os.path.join(export_dir, filename)

    n_rows = max(len(grp[1]) for grp in groups)
    header_parts = []
    for xheader, _, meas_headers, _ in groups:
        header_parts.append(xheader)
        header_parts.extend(meas_headers)

    with open(filepath, "w") as f:
        f.write("\t".join(header_parts) + "\n")
        for row in range(n_rows):
            parts = []
            for _, xvals, _, columns in groups:
                parts.append(str(xvals[row]) if row < len(xvals) else "")
                for col in columns:
                    parts.append(str(col[row]) if row < len(col) else "")
            f.write("\t".join(parts) + "\n")

    n_meas = sum(len(grp[3]) for grp in groups)
    return filepath, n_meas, n_rows


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

    try:
        units = _build_unit_table(project.Units)
    except Exception:
        units = {}
    if not units:
        print("Warning: could not read project units — exporting raw base-unit values.")

    exported = 0
    skipped = 0

    for gi in range(1, graph_count + 1):
        graph = project.Graphs.Item(gi)
        result = _export_graph(graph, export_dir, units)

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
