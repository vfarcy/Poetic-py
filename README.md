Poetic + Bespoke - Python interpreters and website

[![Site GitHub Pages](https://img.shields.io/badge/site-GitHub%20Pages-1f6feb)](https://vfarcy.github.io/Poetic-py/)

This repository contains two esolangs:

- Poetic (Brainfuck-style tape model)
- Bespoke (stack/heap model with structured control flow)

## Overview

Main entry points:

- `poetic.py` - Poetic CLI interpreter
- `bespoke.py` - Bespoke CLI interpreter
- `tests/run_poetic_tests.py` - Poetic smoke tests
- `tests/run_bespoke_tests.py` - Bespoke smoke tests

Language runtimes:

- `tools/poetic/poetic_engine.py`
- `tools/bespoke/bespoke_engine.py`

Example programs:

- `examples/poetic/*.ptc`
- `examples/bespokelang/*.bspk`

Website files:

- `site/`

## Prerequisites

- Python 3.10+

## Run Poetic

Basic usage:

```powershell
python poetic.py examples\poetic\hello.ptc
```

Wimpmode:

```powershell
python poetic.py -w examples\poetic\bonjour.ptc
```

## Run Bespoke

Basic usage:

```powershell
python bespoke.py examples\bespokelang\helloworld.bspk
```

With input file:

```powershell
python bespoke.py -i input.txt examples\bespokelang\sum_two_numbers.bspk
```

## Run Tests

```powershell
python tests\run_poetic_tests.py
python tests\run_bespoke_tests.py
```

## Documentation

- `POETIC_LANGAGE.MD`
- `POETIC_CLI.md`
- `BESPOKE_LANGAGE.MD`
- `BESPOKELANG_CLI.md`
- `CHANGELOG_BESPOKE.md`

## Notes

- The `site/` folder is the website source used for GitHub Pages.
- Historical migration notes remain in `CHANGELOG_BESPOKE.md`.
