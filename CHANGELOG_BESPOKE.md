# Changelog - Bespoke / Poetic documentation and tooling

## 2026-04-08

### Fixed

- `tests/run_poetic_tests.py`
  - Updated example paths to `examples/poetic/*.ptc`
- `tests/run_bespoke_tests.py`
  - Updated example paths to `examples/bespokelang/*.bspk`
- `bespoke.py`
  - Updated import path to `tools.bespoke.bespoke_engine` with backward-compatible fallback

### Documentation updated

- `README.md`
  - Updated to reflect current dual-language repository (Poetic + Bespoke)
  - Corrected runtime and examples paths
  - Corrected test commands (`run_poetic_tests.py`, `run_bespoke_tests.py`)
- `POETIC_CLI.md`
  - Removed obsolete references (`origin/main`, old paths, `tests/run_tests.py`)
  - Updated tool and examples locations to `tools/poetic/` and `examples/poetic/`
- `BESPOKELANG_CLI.md`
  - Removed obsolete references to old runtime/server paths
  - Updated examples and runtime paths to current tree

## 2026-04-07

### Added

- `examples/bespokelang/sum_two_numbers.bspk`
- `examples/bespokelang/loop_10_to_25.bspk`
- `examples/bespokelang/function_call_demo.bspk`

### Notes

- Some historical entries from early migration drafts were removed because they no
  longer matched the current repository state.
