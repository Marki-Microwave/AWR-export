"""Tests for _export_graph using faked COM objects.

Covers legend-name column headers, unit conversion of written values, and
per-x-group file splitting for graphs overlaying traces with different
x-axis sources.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from awr_export import (
    _Unit,
    _export_graph,
    MW_UT_FREQUENCY,
    MW_UT_POWER_LOG,
    MW_UMT_DBM,
)

GHZ = _Unit(MW_UT_FREQUENCY, 9, 1e9, "GHz")
DBM = _Unit(MW_UT_POWER_LOG, MW_UMT_DBM, 1.0, "dBm")
UNITS = {MW_UT_FREQUENCY: GHZ, MW_UT_POWER_LOG: DBM}


class FakeMeasurement:
    def __init__(self, name, xvals, yvals, x_ut=MW_UT_FREQUENCY, y_ut=0):
        self.Name = name
        self.Enabled = True
        self._x = xvals
        self._y = yvals
        self._ut = {1: x_ut, 2: y_ut}

    @property
    def XPointCount(self):
        return len(self._x)

    def XValue(self, i):
        return self._x[i - 1]

    def YValue(self, i, trace):
        return self._y[i - 1]

    def UnitType(self, axis):
        return self._ut[axis]


class FakeTrace:
    def __init__(self, measurement_name, legend_text, use_default=False):
        self.MeasurementName = measurement_name
        self.LegendText = legend_text
        self.UseDefaultLegendText = use_default


class FakeCollection:
    def __init__(self, items):
        self._items = items
        self.Count = len(items)

    def Item(self, i):
        return self._items[i - 1]


class FakeGraph:
    def __init__(self, name, measurements, traces=()):
        self.Name = name
        self.Measurements = FakeCollection(measurements)
        self.Traces = FakeCollection(list(traces))


def read_lines(filepath):
    with open(filepath) as f:
        return [line.rstrip("\n").split("\t") for line in f]


class TestLegendHeaders(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_renamed_trace_uses_legend_plus_param(self):
        m = FakeMeasurement("Verification.AP:DB(|S(2,1)|)", [1e9], [30.0])
        graph = FakeGraph("S21", [m], traces=[
            FakeTrace("Verification.AP:DB(|S(2,1)|)", "11605 MODEL"),
        ])
        results = _export_graph(graph, self.tmp.name, UNITS)
        lines = read_lines(results[0][0])
        self.assertEqual(lines[0], ["Frequency (GHz)", "11605 MODEL - DB(|S(2,1)|)"])

    def test_default_legend_keeps_measurement_name(self):
        m = FakeMeasurement("Verification.AP:DB(|S(2,1)|)", [1e9], [30.0])
        graph = FakeGraph("S21", [m], traces=[
            FakeTrace("Verification.AP:DB(|S(2,1)|)", "Verification.AP:DB(|S(2,1)|)",
                      use_default=True),
        ])
        results = _export_graph(graph, self.tmp.name, UNITS)
        lines = read_lines(results[0][0])
        self.assertEqual(lines[0], ["Frequency (GHz)", "Verification.AP:DB(|S(2,1)|)"])

    def test_duplicate_legend_names_stay_unique(self):
        m1 = FakeMeasurement("A.AP:DB(|S(1,1)|)", [1e9], [-10.0])
        m2 = FakeMeasurement("A.AP:DB(|S(2,1)|)", [1e9], [30.0])
        graph = FakeGraph("SPAR", [m1, m2], traces=[
            FakeTrace("A.AP:DB(|S(1,1)|)", "11605 MEAS"),
            FakeTrace("A.AP:DB(|S(2,1)|)", "11605 MEAS"),
        ])
        results = _export_graph(graph, self.tmp.name, UNITS)
        lines = read_lines(results[0][0])
        self.assertEqual(lines[0], [
            "Frequency (GHz)",
            "11605 MEAS - DB(|S(1,1)|)",
            "11605 MEAS - DB(|S(2,1)|)",
        ])

    def test_measurement_without_trace_keeps_name(self):
        m = FakeMeasurement("A.AP:DB(|S(1,1)|)", [1e9], [-10.0])
        graph = FakeGraph("SPAR", [m])  # no traces at all
        results = _export_graph(graph, self.tmp.name, UNITS)
        lines = read_lines(results[0][0])
        self.assertEqual(lines[0], ["Frequency (GHz)", "A.AP:DB(|S(1,1)|)"])


class TestExportGraph(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_shared_x_grid_single_bare_named_file(self):
        m1 = FakeMeasurement("a:DB(|S(2,1)|)", [1e9, 2e9], [30.0, 31.0])
        m2 = FakeMeasurement("b:DB(|S(1,1)|)", [1e9, 2e9], [-10.0, -12.0])
        graph = FakeGraph("SPAR", [m1, m2])

        results = _export_graph(graph, self.tmp.name, UNITS)
        self.assertEqual(len(results), 1)
        filepath, n_meas, n_rows = results[0]
        self.assertEqual(os.path.basename(filepath), "SPAR.txt")
        self.assertEqual((n_meas, n_rows), (2, 2))

        lines = read_lines(filepath)
        self.assertEqual(lines[0], ["Frequency (GHz)", "a:DB(|S(2,1)|)", "b:DB(|S(1,1)|)"])
        self.assertEqual(lines[1], ["1.0", "30.0", "-10.0"])

    def test_mismatched_x_grids_split_into_files(self):
        measured = FakeMeasurement("file:PlotCol(1,3)", [1e9, 2e9, 3e9], [10.0, 11.0, 12.0])
        simulated = FakeMeasurement("sim:DB(|Pcomp(PORT_2,1)|)", [1.5e9, 2.5e9], [-23.0, -22.0],
                                    y_ut=MW_UT_POWER_LOG)
        graph = FakeGraph("P1dB v Freq", [measured, simulated], traces=[
            FakeTrace("file:PlotCol(1,3)", "11605 MEAS"),
            FakeTrace("sim:DB(|Pcomp(PORT_2,1)|)", "11605 MODEL"),
        ])

        results = _export_graph(graph, self.tmp.name, UNITS)
        self.assertEqual(len(results), 2)

        path1, n_meas1, n_rows1 = results[0]
        self.assertEqual(os.path.basename(path1), "P1dB_v_Freq_-_11605_MEAS.txt")
        self.assertEqual((n_meas1, n_rows1), (1, 3))
        lines = read_lines(path1)
        self.assertEqual(lines[0], ["Frequency (GHz)", "11605 MEAS - PlotCol(1,3)"])
        self.assertEqual(lines[3], ["3.0", "12.0"])

        path2, n_meas2, n_rows2 = results[1]
        self.assertEqual(os.path.basename(path2), "P1dB_v_Freq_-_11605_MODEL.txt")
        self.assertEqual((n_meas2, n_rows2), (1, 2))
        lines = read_lines(path2)
        self.assertEqual(lines[0], ["Frequency (GHz)", "11605 MODEL - DB(|Pcomp(PORT_2,1)|)"])
        # converted (x: Hz->GHz, y: dBW->dBm), rectangular, no padding
        self.assertEqual(lines[1], ["1.5", "7.0"])
        self.assertEqual(lines[2], ["2.5", "8.0"])
        self.assertEqual(len(lines), 3)

    def test_split_label_falls_back_to_group_index(self):
        m1 = FakeMeasurement("a:S(1,1)", [1e9], [1.0])
        m2 = FakeMeasurement("b:S(2,1)", [2e9], [2.0])
        graph = FakeGraph("G", [m1, m2])  # no custom legends

        results = _export_graph(graph, self.tmp.name, UNITS)
        self.assertEqual(os.path.basename(results[0][0]), "G_-_1.txt")
        self.assertEqual(os.path.basename(results[1][0]), "G_-_2.txt")

    def test_no_exportable_data_returns_none(self):
        empty = FakeMeasurement("empty", [], [])
        graph = FakeGraph("Empty", [empty])
        self.assertIsNone(_export_graph(graph, self.tmp.name, UNITS))


if __name__ == "__main__":
    unittest.main()
