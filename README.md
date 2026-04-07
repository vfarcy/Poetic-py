Bespoke (esolang) - Python interpreter + website

[![Site GitHub Pages](https://img.shields.io/badge/site-GitHub%20Pages-1f6feb)](https://vfarcy.github.io/Poetic-py/)

This repository now targets Bespoke as the primary language/runtime.

Migration docs:
- Changelog: CHANGELOG_BESPOKE.md

Overview

This repository contains:
- A Bespoke CLI interpreter: bespoke.py
- A reusable Bespoke runtime: tools/bespoke_engine.py
- Bespoke sample programs: examples/*.bspk
- A local copy of the Bespoke site: site/
- A local HTTP server + API for the website and backend execution: app.py + tools/serve_site.py

Prerequisites

- Python 3.10+ (tested in Windows PowerShell)

Run the Bespoke interpreter

Basic usage:

```powershell
python bespoke.py examples\helloworld.bspk
```

With input file:

```powershell
python bespoke.py -i input.txt examples\fibonacci.bspk
```

Language notes (Bespoke)

- Source is read as UTF-8.
- Words are converted to digit streams by letter count.
- 10-letter words encode digit 0.
- Runtime uses stack + heap and arbitrary-precision integers.
- Structured control flow includes IF, WHILE, DOWHILE, and FUNCTION operations.

Run local website + API

Start local server:

```powershell
python app.py --port 8000
```

Then open:
- Site: http://127.0.0.1:8000/
- Try It Online: http://127.0.0.1:8000/tio/index.html

Backend API (optional)

Endpoint:
- POST /api/run

Request JSON:

```json
{
  "source": "...bespoke source...",
  "input": "...stdin text..."
}
```

Success JSON:

```json
{
  "ok": true,
  "output": "...",
  "steps": 123
}
```

Error JSON (runtime):

```json
{
  "ok": false,
  "error": "..."
}
```

Project structure

- bespoke.py - Bespoke CLI
- app.py - server entry point
- tools/bespoke_engine.py - reusable Bespoke runtime
- tools/serve_site.py - HTTP server + /api/run
- site/ - website pages/assets
- examples/ - Bespoke examples (.bspk)
- tests/run_tests.py - test script

GitHub Pages

- Workflow: .github/workflows/deploy-pages.yml
- Site URL: https://vfarcy.github.io/Poetic-py/
- TIO URL: https://vfarcy.github.io/Poetic-py/tio/index.html
