Poetic (esolang) — Python interpreter + archived website

References

- Internet Archive: https://web.archive.org/web/20210506130651/https://mcaweb.matc.edu/winslojr/vicom128/final/index.html
- Esolang page: https://esolangs.org/wiki/Poetic_(esolang)

Overview

This repository contains:

- A Python interpreter for Poetic: `poetic.py`
- Example Poetic programs: `examples/*.ptc`
- Utility scripts for tokenization/simulation: `tools/`
- A local copy of the original Poetic website: `site/`
- A local server/API to run the Try It Online page: `app.py` + `tools/serve_site.py`

Requirements

- Python 3.10+ (works on Windows PowerShell and standard terminals)

Run the interpreter

Normal mode:

```powershell
python poetic.py examples\hello.ptc
```

With input file:

```powershell
python poetic.py -i input.txt examples\cat.ptc
```

Wimpmode (digits-only source):

```powershell
python poetic.py -w examples\print_A.ptc
```

Poetic language rules implemented

- Source is read as UTF-8.
- Normal mode:
  - non-letter chars become separators (apostrophe is removed),
  - each word becomes its length,
  - length 10 is encoded as `0`.
- Wimpmode (`-w`): keep only digits.
- Tokenization regex:

```python
re.findall(r"((?:[3456]\d)|\d)", program)
```

Instructions

- `0` END
- `1` IF
- `2` EIF
- `3x` INC x (`0` arg means 10)
- `4x` DEC x (`0` arg means 10)
- `5x` FWD x (`0` arg means 10)
- `6x` BAK x (`0` arg means 10)
- `7` OUT
- `8` IN
- `9` RND

Runtime semantics

- Tape size: 30000 bytes
- Byte values wrap modulo 256
- Pointer wraps modulo tape size
- IF/EIF supports nesting
- IN stops modifying memory after EOF/CTRL+Z

Common errors from interpreter

- `Unexpected EOF`
- `Missing argument`
- `Mismatched IF/EIF`

Utilities

- `tools/tokenize.py`
  - Print tokens from a file using the same parsing rules as `poetic.py`
- `tools/simulate.py`
  - Step-by-step simulation with execution trace
- `tools/simulate_text.py`
  - Simulate from `--text` directly (no temporary file needed)

Examples:

```powershell
python tools\tokenize.py examples\hello.ptc
python tools\simulate.py -w --simulate examples\print_A.ptc
python tools\simulate_text.py --text "bonjour le monde" --tokens
```

Website (archived copy) and Try It Online

The `site/` folder is a local reconstruction of the original website (pages, styles, fonts, textures).

Run local web server + API:

```powershell
python app.py --port 8000
```

Then open:

- Main site: http://127.0.0.1:8000/
- Try It Online: http://127.0.0.1:8000/tio/index.html

API endpoint used by TIO

- `POST /api/run`
- JSON body:

```json
{
  "source": "...poetic source...",
  "input": "...stdin text...",
  "wimpmode": false
}
```

- JSON response (success):

```json
{
  "ok": true,
  "output": "...",
  "steps": 123,
  "tokens": 45
}
```

Notes on the TIO page

- `Execute` runs code through `/api/run`.
- `Stop` aborts the browser request.
- `Wimpmode OFF/ON` toggles digit-mode execution.
- `Share` creates a link that stores source/input/wimpmode in URL state.
- API status indicator shows Connected/Disconnected and supports Retry.

Project layout

- `poetic.py` — CLI interpreter
- `app.py` — root launcher for website server
- `tools/poetic_engine.py` — reusable Poetic runtime for API
- `tools/serve_site.py` — HTTP server + `/api/run`
- `site/` — archived website pages/assets (including `site/tio/index.html`)
- `examples/` — `.ptc` samples
- `tests/run_tests.py` — test runner

Quick troubleshooting

- If port 8000 is busy, use another port:

```powershell
python app.py --port 8011
```

- Then open the matching URL (`http://127.0.0.1:8011/tio/index.html`).
