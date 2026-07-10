# Legend-name headers and per-x-group export files

Date: 2026-07-09
Status: approved

## Problem

1. Users rename traces in AWR (Graph Properties > Legend Measurement Name),
   but exports use the raw measurement name (`Source:PARAM(...)`) as the
   column header.
2. Graphs overlaying traces with different x-axis sources (e.g. measured
   file data + simulated sweep) currently export side-by-side padded
   columns in one file — two interleaved x columns with trailing blanks.

## Design

### Column headers from legend names

- Build a per-graph map `Trace.MeasurementName -> Trace.LegendText` for
  traces where `UseDefaultLegendText` is False and the text is non-empty.
- Renamed trace header: `<legend> - <param>` where `<param>` is
  `Measurement.Name` with the `Source:` prefix stripped (the legend name
  already identifies the source). Example: `11605 MEAS - DB(|S(2,1)|)`.
  The uniform `legend + param` format keeps headers unique when several
  traces share a legend name (e.g. S11/S21/S22 all renamed "11605 MEAS").
- Default-legend traces keep the full `Measurement.Name` header (the
  default legend text is the measurement name; combining would duplicate).
- No colon is introduced, so `MWO_Parser` keeps the whole header as the
  column name.

### One file per x-group

- Measurements are already grouped by identical x-vector (v1.1.0).
- Single group (the common case): one file, `<Graph>.txt`, format
  byte-identical to v1.1.0.
- Multiple groups: one file per group, `<Graph> - <label>.txt`. Every
  file gets a suffix so a partial file is never mistaken for the whole
  graph. Label = the group's first column's legend name (sanitized);
  fallback = the group's 1-based index. Duplicate labels get the index
  appended.
- Each file is a clean rectangular table — no padding cells. Within a
  group all columns share the x-vector, so lengths always match.
- Console output lists every file written.

## Consequences

- Downstream scripts keyed to raw measurement-name columns must switch to
  the new names for renamed traces (intended: headers match the graph).
- `_export_graph` returns a list of file paths (was a single path);
  `export_all_graph_traces` prints them per graph.

## Testing

Extend the fake-COM suite: renamed / default / duplicated legend names;
single-group naming regression; multi-group file naming, labels, and
fallback; rectangular output (no padding) per file.
