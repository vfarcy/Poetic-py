# Changelog - Poetic to Bespoke migration

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

- Legacy Poetic documentation remains in existing files for historical context.
- Branch target for this migration: `bespokelang`.
