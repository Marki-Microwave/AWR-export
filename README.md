# AWR-export

Export every open graph in an AWR Design Environment (Microwave Office) project to tab-separated `.txt` files — one file per graph, with all enabled measurements as columns.

Built for engineers who want plottable, parseable trace data out of AWR without clicking through `Export Trace Data` on every graph.

## What it does

- Connects to a running AWR / Microwave Office instance via COM.
- Walks every graph in the open project.
- Reads measurement data directly from each enabled measurement (`XValue` / `YValue`) and writes a tab-separated file per graph.
- Auto-detects frequency-domain X axes and converts Hz → GHz in the header.
- Skips graphs with no exportable data instead of failing.

This bypasses AWR's `ExportTraceData` COM method, which crashes the application when called from an external process. Reading values directly from the measurement objects is stable.

## Quick start

### Option 1 — prebuilt executable (recommended for end users)

1. Open your AWR project and run all simulations so the graphs have data.
2. Go to the [Releases page](https://github.com/Marki-Microwave/AWR-export/releases) and download `awr_export-windows-x64.zip`.
3. **Extract the entire zip** to a folder of your choice (Desktop, Documents, etc.). You should end up with an `awr_export/` folder containing `awr_export.exe` and an `_internal/` subfolder. **Both are required** — `awr_export.exe` will not run without the `_internal/` folder sitting next to it.
4. Double-click `awr_export.exe`. A folder picker appears — choose where to save the exported files.
5. Done. One `.txt` per graph appears in the chosen folder.

> ⚠️ Do not pull `awr_export.exe` out of the extracted folder. It depends on dozens of DLLs and Python files in `_internal/`. If you want a desktop shortcut, right-click `awr_export.exe` → *Send to* → *Desktop (create shortcut)*.

### Option 2 — from source

```sh
git clone https://github.com/Marki-Microwave/AWR-export.git
cd AWR-export
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Open AWR, load a project, run simulations, then:
python main.py export
```

## CLI usage

```
awr_export.exe                     # default: export — opens folder picker
awr_export.exe export              # explicit export
awr_export.exe export --output-dir C:\path\to\folder
awr_export.exe parse FILE.txt      # parse a previously exported file and print a summary
```

## Output format

Each graph becomes one tab-separated file named after the graph (illegal Windows characters are sanitized to `_`):

```
Frequency (GHz)    S(2,1)    S(1,1)    S(2,2)
1.0                -0.31     -22.4     -25.1
1.5                -0.29     -23.0     -24.8
...
```

- First column is the X axis (auto-labeled `Frequency (GHz)` if X values exceed 1 MHz, otherwise `X`).
- One column per enabled measurement.
- Disabled measurements and graphs with no data are skipped.

## Requirements

- Windows (AWR / Microwave Office is Windows-only)
- AWR Design Environment / Microwave Office installed and running with a project open
- Running from source: Python 3.13+ and the packages in `requirements.txt`

## Building the executable

```sh
pip install pyinstaller
pyinstaller awr_export.spec
```

The bundled app appears in `dist/awr_export/`. Distribute the **entire folder** — `awr_export.exe` depends on the `_internal/` directory next to it. To publish a release, zip `dist/awr_export/` (so the zip root is the `awr_export/` folder) and upload it as a release asset.

## Repo layout

```
main.py             Unified CLI entry point (export / parse subcommands)
awr_export.py       Core COM export logic
MWO_Parser.py       Parser for AWR-exported tab-separated data files
data_handle.py      Helper for batch-loading Keysight VNA CSVs (legacy utility)
awr_export.spec     PyInstaller build specification
requirements.txt    Python dependencies

scripts/            AWR Script Editor (.bas) macros — alternative export path
tools/              COM connectivity diagnostics
examples/           Demo / smoke-test scripts (large datasets gitignored)
```

## Why a CLI tool instead of a Script Editor macro?

Both work. The `.bas` macros in `scripts/` run inside AWR and are useful when you can't install Python on the host, but they require pasting the macro into the Script Editor every time. This CLI runs externally, leaves no footprint inside the project, and ships as a single double-clickable executable for non-developer users.

## License

Internal — Marki Microwave.
