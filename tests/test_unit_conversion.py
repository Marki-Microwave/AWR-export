"""Tests for base-unit -> display-unit conversion in awr_export.

AWR COM XValue/YValue return base units (Hz, W, V, dBW...). Graphs display
per the project's Units table. These tests cover the generic conversion,
driven only by (Type, MultType, MultValue) as AWR reports them.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from awr_export import (
    _Unit,
    _build_unit_table,
    _to_display,
    MW_UT_FREQUENCY,
    MW_UT_TEMPERATURE,
    MW_UT_CURRENT,
    MW_UT_POWER_LOG,
    MW_UT_POWER,
    MW_UT_DB,
    MW_UT_DB_ONLY_POWER,
    MW_UMT_DEGC,
    MW_UMT_DEGK,
    MW_UMT_DBM,
    MW_UMT_DBW,
)


def unit(utype, mult_type=6, mult_value=1.0, unit_string=""):
    return _Unit(utype, mult_type, mult_value, unit_string)


class TestToDisplay(unittest.TestCase):
    def test_log_power_dbm_adds_30(self):
        # base is dBW; graph shows dBm
        u = unit(MW_UT_POWER_LOG, mult_type=MW_UMT_DBM, unit_string="dBm")
        self.assertAlmostEqual(_to_display(-10.0, u), 20.0)

    def test_log_power_dbw_unchanged(self):
        u = unit(MW_UT_POWER_LOG, mult_type=MW_UMT_DBW, unit_string="dBW")
        self.assertAlmostEqual(_to_display(-10.0, u), -10.0)

    def test_db_only_power_dbm_adds_30(self):
        u = unit(MW_UT_DB_ONLY_POWER, mult_type=MW_UMT_DBM, unit_string="dBm")
        self.assertAlmostEqual(_to_display(0.0, u), 30.0)

    def test_linear_current_milliamps(self):
        # 0.005 A displayed as 5 mA
        u = unit(MW_UT_CURRENT, mult_value=1e-3, unit_string="mA")
        self.assertAlmostEqual(_to_display(0.005, u), 5.0)

    def test_linear_power_milliwatts(self):
        u = unit(MW_UT_POWER, mult_value=1e-3, unit_string="mW")
        self.assertAlmostEqual(_to_display(0.02, u), 20.0)

    def test_frequency_gigahertz(self):
        u = unit(MW_UT_FREQUENCY, mult_value=1e9, unit_string="GHz")
        self.assertAlmostEqual(_to_display(2.4e9, u), 2.4)

    def test_dimensionless_db_unchanged(self):
        u = unit(MW_UT_DB, mult_value=1.0, unit_string="dB")
        self.assertAlmostEqual(_to_display(-13.7, u), -13.7)

    def test_temperature_kelvin_to_celsius(self):
        u = unit(MW_UT_TEMPERATURE, mult_type=MW_UMT_DEGC, unit_string="DegC")
        self.assertAlmostEqual(_to_display(300.0, u), 26.85)

    def test_temperature_kelvin_unchanged(self):
        u = unit(MW_UT_TEMPERATURE, mult_type=MW_UMT_DEGK, unit_string="K")
        self.assertAlmostEqual(_to_display(300.0, u), 300.0)

    def test_zero_mult_value_is_passthrough(self):
        u = unit(MW_UT_DB, mult_value=0.0)
        self.assertAlmostEqual(_to_display(1.5, u), 1.5)

    def test_none_unit_is_passthrough(self):
        self.assertAlmostEqual(_to_display(1.5, None), 1.5)


class FakeComUnit:
    def __init__(self, utype, mult_type, mult_value, unit_string):
        self.Type = utype
        self.MultType = mult_type
        self.MultValue = mult_value
        self.UnitString = unit_string


class FakeUnits:
    def __init__(self, items):
        self._items = items
        self.Count = len(items)

    def Item(self, i):  # 1-based, like COM
        return self._items[i - 1]


class TestBuildUnitTable(unittest.TestCase):
    def test_table_keyed_by_unit_type(self):
        com_units = FakeUnits([
            FakeComUnit(MW_UT_FREQUENCY, 9, 1e9, "GHz"),
            FakeComUnit(MW_UT_POWER_LOG, MW_UMT_DBM, 1e-3, "dBm"),
        ])
        table = _build_unit_table(com_units)
        self.assertEqual(table[MW_UT_FREQUENCY].unit_string, "GHz")
        self.assertEqual(table[MW_UT_POWER_LOG].mult_type, MW_UMT_DBM)
        self.assertAlmostEqual(table[MW_UT_FREQUENCY].mult_value, 1e9)

    def test_broken_entry_is_skipped(self):
        class Exploding:
            @property
            def Type(self):
                raise OSError("COM error")

        com_units = FakeUnits([
            Exploding(),
            FakeComUnit(MW_UT_DB, 6, 1.0, "dB"),
        ])
        table = _build_unit_table(com_units)
        self.assertNotIn(MW_UT_FREQUENCY, table)
        self.assertEqual(table[MW_UT_DB].unit_string, "dB")


if __name__ == "__main__":
    unittest.main()
