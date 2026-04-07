# Changelog - Poetic to Bespoke migration

## 2026-04-07 (site & CLI polish)

Scope: examples, site pages, and CLI fixes after initial migration.

### Added

- `examples/sum_two_numbers.bspk` — reads two integers from stdin, outputs their sum
- `examples/loop_10_to_25.bspk` — loop from 10 to 25, each number on its own line (encoded as French prose)
- `examples/function_call_demo.bspk` — minimal FUNCTION/CALL demo, outputs 42

### Fixed

- `bespoke.py`
  - CLI no longer blocks waiting for stdin when launched from an interactive terminal (`sys.stdin.isatty()` guard)

### Updated

- `BESPOKELANG_CLI.md`
  - Added HTTP status codes (200/400/404/500), CORS/OPTIONS behavior, and runtime limits (`max_steps`, `max_output`, `time_limit_s`)
- `site/download/index.html`
  - Corrected GitHub link (now `vfarcy/Poetic-py`), removed PyPI/pip reference, added `git clone` command and pipe usage examples
- `site/index.html`
  - Updated attribution paragraph: correct GitHub link, note that this site is a web implementation of Josiah Winslow's original project, added TIO link
- `site/contact/index.html`
  - Replaced personal contact details (email, Twitter) with links to `vfarcy/Poetic-py` Issues and Pull Requests
- `site/tutorial/index.html`
  - Removed appended legacy Poetic tutorial block (source code rules, Brainfuck instruction set, clarifications)

## 2026-04-07 (cleanup)

Scope: remove remaining Poetic legacy files now that `.ptc` programs are gone.

### Removed

- `poetic.py`
- `tools/poetic_engine.py`
- `tools/simulate.py`
- `tools/simulate_text.py`
- `tools/tokenize.py`
- `README_POETIC_LEGACY.md`

### Updated

- `tests/run_tests.py`
  - Replaced Poetic tests with Bespoke smoke tests:
    - `examples/helloworld.bspk`
    - `examples/sum_two_numbers.bspk`
    - `examples/truth.bspk` (input `0`)
- `README.md`
  - Removed reference to legacy Poetic notes

## 2026-04-07

Scope: replace Poetic with Bespoke on branch `bespokelang`, while preserving the
existing website structure/style.

### Added

- `tools/bespoke_engine.py`: self-contained Bespoke interpreter runtime
- `bespoke.py`: command-line entry point for Bespoke
- `examples/helloworld.bspk`
- `examples/fibonacci.bspk`
- `examples/truth.bspk`
- `examples/asciiloop.bspk`

### Changed

- `tools/serve_site.py`
  - Switched backend execution from Poetic to Bespoke
  - API `POST /api/run` now runs `run_bespoke(...)`
  - Removed Poetic wimpmode handling
- `site/index.html`
  - Rebranded to BESPOKE
  - Updated home content and quick usage examples
- `site/tutorial/index.html`
  - Rewritten for Bespoke instruction model and control flow
- `site/examples/index.html`
  - Replaced Poetic examples with Bespoke examples
- `site/tio/index.html`
  - Replaced client-side engine with a Bespoke BigInt interpreter
  - Removed wimpmode UI and behavior
- `site/download/index.html`
  - Updated install/CLI instructions to Bespoke
- `site/faq/index.html`
  - Updated FAQ entries to Bespoke concepts
- `site/contact/index.html`
  - Rebranded and refreshed contact wording
- `README.md`
  - Rewritten as Bespoke-first project documentation
  - Removed Poetic-focused operational details from the main entry point

### Documentation

- `README_POETIC_LEGACY.md`
  - Added as historical Poetic reference after README migration

### Validation

- Local smoke test passed:
  - `GET /tio/index.html` returned HTTP 200
  - `POST /api/run` executed Bespoke source successfully

### Notes

- Branch target for this migration: `bespokelang`.
