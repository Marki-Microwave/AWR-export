# AWR Project Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up and consolidate the AWR trace export project into a well-structured, robust tool with a single entry point, fixed bugs, and proper packaging.

**Architecture:** Promote `Arch_API_tests/main.py` (COM export) into the root as `awr_export.py`. Fix known bugs in `data_handle.py`. Clean up `MWO_Parser.py`. Retire `Arch_API_tests/` directory (move test utilities to `tools/`). Replace root `main.py` with a unified CLI entry point. Add `requirements.txt`.

**Tech Stack:** Python 3.10, pywin32 (COM), pandas, numpy, matplotlib, tkinter

---

## Task 1: Harden and promote AWR COM export

The core AWR export logic lives in `Arch_API_tests/main.py`. It needs to be promoted to the project root as `awr_export.py` with proper resource cleanup, filename sanitization, and error handling.

**Files:**
- Create: `awr_export.py` (promoted from `Arch_API_tests/main.py`)
- Delete: `Arch_API_tests/main.py` (replaced by above)

**What to fix:**
- Add `try/finally` to close the project and optionally quit AWR
- Sanitize filenames: replace characters illegal on Windows (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) with `_`
- Handle duplicate trace names by appending `_N` suffix
- Print summary at end (count of exported, count of failed)
- Keep the same public API: `export_all_graph_traces(project_path=None, export_dir=None)`

- [ ] **Step 1:** Create `awr_export.py` at project root with hardened export logic
- [ ] **Step 2:** Verify the file is syntactically valid: `python -c "import ast; ast.parse(open('awr_export.py').read()); print('OK')"`
- [ ] **Step 3:** Commit: `git add awr_export.py && git commit -m "feat: promote and harden AWR COM export"`

---

## Task 2: Fix bugs in data_handle.py

`data_handle.py` has several bugs and code quality issues.

**Files:**
- Modify: `data_handle.py`

**Bugs to fix:**
1. **Line 98 — `smooth_data` off-by-one:** `len(data[0] - n - 1)` applies subtraction to the numpy array, not its length. Fix to `len(data[0]) - n - 1`.
2. **Line 161, 170 — `trim`/`trim_low` unused variable:** `xi_o = 0` is assigned but never used; the code actually uses `xi_0`. Remove the dead `xi_o` assignments.
3. **Hardcoded `"\\"` path separators** on lines 39, 219, 240: Replace with `os.path.join()`.
4. **String sentinel defaults** in `plot_data` and `overplot`: Replace `"default"` sentinels with `None` and update the corresponding `isinstance(x, str)` checks to `x is not None`.

- [ ] **Step 1:** Fix `smooth_data` bug on line 98
- [ ] **Step 2:** Fix dead `xi_o` variable in `trim` and `trim_low` blocks
- [ ] **Step 3:** Replace hardcoded `"\\"` path joins with `os.path.join()`
- [ ] **Step 4:** Replace `"default"` string sentinels with `None` in `plot_data` and `overplot`
- [ ] **Step 5:** Verify syntax: `python -c "import ast; ast.parse(open('data_handle.py').read()); print('OK')"`
- [ ] **Step 6:** Commit: `git add data_handle.py && git commit -m "fix: bugs in data_handle — smooth_data, paths, sentinels"`

---

## Task 3: Clean up MWO_Parser.py

Minor quality improvements to the parser.

**Files:**
- Modify: `MWO_Parser.py`

**What to fix:**
1. Multiple colons in column headers — `split(':', 1)` is correct but the guard `if ':' in col` should use the same maxsplit to avoid inconsistency. Actually the current logic is fine on split, but if a column name has no colon, `cleaned_name` still gets mapped. The real issue: if two columns clean to the same name (e.g., `"Gain:trace1"` and `"Gain:trace2"` both become `"Gain"`), the second silently overwrites the first in `column_mapping`. Add duplicate detection — append `_N` suffix when a cleaned name already exists.
2. Tkinter root window leak — `root = tk.Tk()` is created but `root.destroy()` is never called after the dialog closes. Add cleanup.

- [ ] **Step 1:** Fix duplicate column name handling in `_parse()`
- [ ] **Step 2:** Fix tkinter root leak in `_get_file_via_dialog()`
- [ ] **Step 3:** Verify syntax: `python -c "import ast; ast.parse(open('MWO_Parser.py').read()); print('OK')"`
- [ ] **Step 4:** Commit: `git add MWO_Parser.py && git commit -m "fix: duplicate column names and tkinter leak in MWO_Parser"`

---

## Task 4: Move COM test utilities and archive demo script

The `Arch_API_tests/` test files are useful diagnostic tools but shouldn't live at the top level with a confusing name. Move them to `tools/`. The `PE15_OP_TestStructrePlots.py` demo script has hardcoded paths — move to `examples/`.

**Files:**
- Create: `tools/test_com_connect.py` (from `Arch_API_tests/testA.py`)
- Create: `tools/test_com_dispatch.py` (from `Arch_API_tests/testcom.py`)
- Create: `tools/test_com_classnames.py` (from `Arch_API_tests/testcom2.py`)
- Create: `examples/pe15_test_structure_plots.py` (from `PE15_OP_TestStructrePlots.py`)
- Delete: `Arch_API_tests/` directory (all files moved)
- Delete: `PE15_OP_TestStructrePlots.py` (moved)

- [ ] **Step 1:** Create `tools/` directory and move the three test files with clearer names
- [ ] **Step 2:** Create `examples/` directory and move the demo script
- [ ] **Step 3:** Delete `Arch_API_tests/` directory and root-level `PE15_OP_TestStructrePlots.py`
- [ ] **Step 4:** Commit: `git add -A && git commit -m "refactor: reorganize — tools/ for COM diagnostics, examples/ for demo scripts"`

---

## Task 5: Unified entry point and requirements

Replace the stub `main.py` with a proper CLI that ties the project together. Add `requirements.txt`.

**Files:**
- Modify: `main.py` (rewrite)
- Create: `requirements.txt`

**`main.py` behavior:**
- `python main.py export` — runs `awr_export.export_all_graph_traces()`
- `python main.py parse <file>` — runs `MWO_Parser.APFileParser(file)` and prints summary
- No args / `python main.py --help` — prints usage
- Use `argparse` for CLI parsing

**`requirements.txt`:**
```
pandas>=2.0
numpy>=2.0
matplotlib>=3.8
pywin32>=306
```

- [ ] **Step 1:** Write `requirements.txt`
- [ ] **Step 2:** Rewrite `main.py` as a CLI entry point with argparse
- [ ] **Step 3:** Verify syntax: `python -c "import ast; ast.parse(open('main.py').read()); print('OK')"`
- [ ] **Step 4:** Verify help output: `python main.py --help`
- [ ] **Step 5:** Commit: `git add main.py requirements.txt && git commit -m "feat: unified CLI entry point and requirements.txt"`
