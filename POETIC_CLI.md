# POETIC_CLI

Ce document decrit le fonctionnement de `poetic.py`.

## 1) Vue d'ensemble

Le projet fournit:

- Un interpreteur Poetic en Python: `poetic.py`
- Des exemples de programmes Poetic: `examples/poetic/*.ptc`
- Des outils de debug/tokenisation/simulation: `tools/poetic/`
- Un script de test: `tests/run_poetic_tests.py`

## 2) Prerequis

- Python 3.10+
- Aucune dependance externe obligatoire (standard library uniquement)

## 3) Interpreteur principal (`poetic.py`)

### 3.1 Lancement

Commande generale:

```powershell
python poetic.py [ -i input-file ] [ -w ] poetic-program
```

Arguments:

- `poetic-program` (obligatoire): fichier source a executer
- `-i`, `--input` (optionnel): lire l'entree depuis un fichier au lieu de STDIN
- `-w`, `--wimpmode` (optionnel): interpreter le source comme une suite de chiffres

Exemples:

```powershell
python poetic.py examples\poetic\hello.ptc
python poetic.py -w examples\poetic\print_A.ptc
python poetic.py -i input.txt examples\poetic\cat.ptc
```

### 3.2 Parsing / tokenisation

Mode normal:

1. Lecture UTF-8 du fichier
2. Remplacement des caracteres non alphabetiques par espace
3. Suppression des apostrophes `'`
4. Split en mots
5. Conversion des mots en longueurs (`10` devient `0`)
6. Extraction des tokens via:

```python
re.findall(r"((?:[3456]\d)|\d)", program)
```

Mode wimpmode (`-w`):

- Conservation des chiffres `0-9` uniquement
- Meme regex ensuite

### 3.3 Machine d'execution

Etat runtime:

- `memory = bytearray(30000)`
- `memoryPointer` avec wrap-around modulo 30000
- Cellules sur 8 bits (modulo 256)
- `instructionPointer`
- `eofReached`

### 3.4 Jeu d'instructions

- `0` END
- `1` IF
- `2` EIF
- `3x` INC
- `4x` DEC
- `5x` FWD
- `6x` BAK
- `7` OUT
- `8` IN
- `9` RND

## 4) Outils Poetic

Scripts disponibles dans `tools/poetic/`:

- `tokenize.py`
- `simulate.py`
- `simulate_text.py`
- `poetic_engine.py`

Exemples:

```powershell
python tools\poetic\tokenize.py examples\poetic\hello.ptc
python tools\poetic\simulate.py --simulate examples\poetic\hello.ptc
python tools\poetic\simulate_text.py --text "bonjour le monde" --tokens
```

## 5) Exemples Poetic

Fichiers dans `examples/poetic/`:

- `hello.ptc`
- `bonjour.ptc`
- `cat.ptc`
- `tupni.ptc`
- `asciiloop.ptc`
- `random.ptc`
- `print_A.ptc`
- `print_bang.ptc`

## 6) Tests

Le runner Poetic valide:

1. `hello.ptc` (mode normal) -> `Hello World!`
2. `bonjour.ptc` (mode wimpmode) -> `bonjour!`

Execution:

```powershell
python tests\run_poetic_tests.py
```
