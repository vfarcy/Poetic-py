# BESPOKELANG_CLI

Ce document decrit le fonctionnement du CLI Bespoke implemente dans `bespoke.py`.

## 1) Vue d'ensemble

Le projet fournit:

- Un interpreteur Bespokelang en Python: `bespoke.py`
- Un runtime reutilisable: `tools/bespoke/bespoke_engine.py`
- Des exemples Bespoke: `examples/bespokelang/*.bspk`
- Un script de tests: `tests/run_bespoke_tests.py`

## 2) Prerequis

- Python 3.10+
- Aucune dependance externe obligatoire (standard library uniquement)

## 3) Interpreteur principal (`bespoke.py`)

### 3.1 Lancement

Commande generale:

```powershell
python bespoke.py [ -i input-file ] program.bspk
```

Arguments:

- `program.bspk` (obligatoire): fichier source Bespoke
- `-i`, `--input` (optionnel): lire l'entree depuis un fichier au lieu de STDIN

Exemples:

```powershell
python bespoke.py examples\bespokelang\helloworld.bspk
python bespoke.py -i input.txt examples\bespokelang\sum_two_numbers.bspk
```

### 3.2 Pipeline d'execution

Le runtime suit ces etapes:

1. Conversion texte -> flux de chiffres via longueur des mots (`convert_to_digits`)
2. Tokenisation (`_tokenize`)
3. Construction d'AST avec blocs de controle (`_create_ast`)
4. Interpretation avec pile, tas, fonctions et signaux de controle

Implementation: `tools/bespoke/bespoke_engine.py`.

### 3.3 Entree / sortie

- Si `-i` est absent, l'entree est lue depuis STDIN.
- `INPUT N` lit un entier signe.
- `INPUT CH` lit un caractere et pousse son codepoint (ou `-1` en EOF).
- `OUTPUT N` ecrit un entier texte.
- `OUTPUT CH` ecrit un caractere Unicode.

### 3.4 Erreurs courantes

Les erreurs runtime remontent comme `BespokeRuntimeError`, par exemple:

- `Stack underflow`
- `Invalid stack argument: ...`
- `Undefined function: ...`
- `Division by zero` / `Modulo by zero`
- `Unexpected CONTROL END`
- `Unexpected CONTROL OTHERWISE`
- `RETURN outside of function`
- `BREAK outside of loop`

## 4) Categories d'instructions Bespoke

Le langage code ses operations avec les categories `0..9`:

- `0`: COMMENTARY
- `1`: H (heap)
- `2`: DO (manipulation de pile)
- `3`: PUT (nombre multi-chiffres)
- `4`: PUSH (chiffre simple)
- `5`: INPUT
- `6`: OUTPUT
- `7`: CONTROL
- `8`: STACKTOP (operations arithmetiques/logiques)
- `9`: CONTINUED (extension de nombre/nom)

Remarques:

- Les entiers sont en precision arbitraire.
- `CONTROL IF`, `CONTROL WHILE`, `CONTROL DOWHILE`, `CONTROL FUNCTION` sont geres via AST.
- `CONTINUED` permet d'etendre un litteral (`PUT`) ou un nom de fonction (`CALL`/`FUNCTION`).

## 5) Exemples disponibles

- `examples/bespokelang/helloworld.bspk`
- `examples/bespokelang/fibonacci.bspk`
- `examples/bespokelang/truth.bspk`
- `examples/bespokelang/asciiloop.bspk`
- `examples/bespokelang/function_call_demo.bspk`
- `examples/bespokelang/loop_10_to_25.bspk`
- `examples/bespokelang/sum_two_numbers.bspk`

Commandes rapides:

```powershell
python bespoke.py examples\bespokelang\helloworld.bspk
python bespoke.py examples\bespokelang\truth.bspk
python tests\run_bespoke_tests.py
```

## 6) Note serveur local

Le site statique est dans `site/`.
Les scripts de serveur (`app.py` et `tools/bespoke/serve_site.py`) existent, mais leur
configuration d'import/chemins doit etre harmonisee avant d'etre documentee comme
point d'entree stable.
