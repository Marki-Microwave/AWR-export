"""Tests for _export_graph using faked COM objects.

Covers the mixed-grid case (e.g. a 201-point measured-data trace overlaid
with a 161-point simulated sweep on the same graph) and unit conversion of
written values.
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


class FakeCollection:
    def __init__(self, items):
        self._items = items
        self.Count = len(items)

    def Item(self, i):
        return self._items[i - 1]


class FakeGraph:
    def __init__(self, name, measurements):
        self.Name = name
        self.Measurements = FakeCollection(measurements)


def read_lines(filepath):
    with open(filepath) as f:
        return [line.rstrip("\n").split("\t") for line in f]


class TestExportGraph(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_mismatched_x_grids_get_own_x_columns(self):
        measured = FakeMeasurement("file:PlotCol(1,3)", [1e9, 2e9, 3e9], [10.0, 11.0, 12.0])
        simulated = FakeMeasurement("sim:DB(|Pcomp(PORT_2,1)|)", [1.5e9, 2.5e9], [-23.0, -22.0],
                                    y_ut=MW_UT_POWER_LOG)
        graph = FakeGraph("P1dB v Freq", [measured, simulated])

        result = _export_graph(graph, self.tmp.name, UNITS)
        self.assertIsNotNone(result)
        filepath, n_meas, n_rows = result
        self.assertEqual(n_meas, 2)
        self.assertEqual(n_rows, 3)

        lines = read_lines(filepath)
        self.assertEqual(lines[0], [
            "Frequency (GHz)", "file:PlotCol(1,3)",
            "Frequency (GHz)", "sim:DB(|Pcomp(PORT_2,1)|)",
        ])
        # second group converted (x: Hz->GHz, y: dBW->dBm)
        self.assertEqual(lines[1], ["1.0", "10.0", "1.5", "7.0"])
        self.assertEqual(lines[2], ["2.0", "11.0", "2.5", "8.0"])
        # shorter group padded with empty cells
        self.assertEqual(lines[3], ["3.0", "12.0", "", ""])

    def test_shared_x_grid_stays_single_column(self):
        m1 = FakeMeasurement("a:DB(|S(2,1)|)", [1e9, 2e9], [30.0, 31.0])
        m2 = FakeMeasurement("b:DB(|S(1,1)|)", [1e9, 2e9], [-10.0, -12.0])
        graph = FakeGraph("SPAR", [m1, m2])

        filepath, n_meas, n_rows = _export_graph(graph, self.tmp.name, UNITS)
        self.assertEqual((n_meas, n_rows), (2, 2))

        lines = read_lines(filepath)
        self.assertEqual(lines[0], ["Frequency (GHz)", "a:DB(|S(2,1)|)", "b:DB(|S(1,1)|)"])
        self.assertEqual(lines[1], ["1.0", "30.0", "-10.0"])

    def test_no_exportable_data_returns_none(self):
        empty = FakeMeasurement("empty", [], [])
        graph = FakeGraph("Empty", [empty])
        self.assertIsNone(_export_graph(graph, self.tmp.name, UNITS))


if __name__ == "__main__":
    unittest.main()
