# MANUAL - Poetic-py (source: origin/main)

Ce document decrit l'etat de la branche `main` du depot `vfarcy/Poetic-py`.
Il ne decrit pas les ajouts de branches de travail (site local, serveur web, etc.).

## 1) Vue d'ensemble

Le projet fournit:

- Un interpreteur Poetic en Python: `poetic.py`
- Des exemples de programmes Poetic: `examples/*.ptc`
- Des outils de debug/tokenisation/simulation dans `tools/`
- Un script de test simple dans `tests/run_tests.py`

Fichiers presents sur `origin/main`:

- `.gitignore`
- `README.md`
- `poetic.py`
- `examples/asciiloop.ptc`
- `examples/bonjour.ptc`
- `examples/cat.ptc`
- `examples/hello.ptc`
- `examples/print_A.ptc`
- `examples/print_bang.ptc`
- `examples/random.ptc`
- `examples/tupni.ptc`
- `tools/tokenize.py`
- `tools/simulate.py`
- `tools/simulate_text.py`
- `tests/run_tests.py`

## 2) Prerequis

- Python 3.x
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
python poetic.py examples\hello.ptc
python poetic.py -w examples\print_A.ptc
python poetic.py -i input.txt examples\cat.ptc
```

### 3.2 Parsing / tokenisation

Mode normal:

1. Lecture UTF-8 du fichier
2. Remplacement des caracteres non alphabetiques par espace
3. Suppression des apostrophes `'`
4. Split en mots
5. Conversion des mots en longueurs:
   - longueur `10` -> chiffre `0`
   - sinon la longueur numerique normale
6. Extraction des tokens avec:

```python
re.findall(r"((?:[3456]\d)|\d)", program)
```

Mode wimpmode (`-w`):

- On conserve uniquement les chiffres `0-9` du fichier
- Meme regex de tokenisation ensuite

Interpretation des tokens:

- Token 1 chiffre: opcode seul (ex: `7`)
- Token 2 chiffres autorise seulement si premier chiffre `3`, `4`, `5`, `6` (opcode + argument)
- Argument `0` est interprete comme `10`

### 3.3 Machine d'execution

Etat runtime:

- `memory = bytearray(30000)`
- `memoryPointer` avec wrap-around modulo 30000
- valeurs de cellule en modulo 256
- `instructionPointer`
- `eofReached` pour gerer la fin d'entree

### 3.4 Jeu d'instructions

- `0` END: fin execution
- `1` IF: si cellule courante == 0, saute apres EIF correspondant
- `2` EIF: si cellule courante != 0, revient avant IF correspondant
- `3x` INC: ajoute `x` (ou 10 si x=0)
- `4x` DEC: soustrait `x` (ou 10 si x=0)
- `5x` FWD: avance pointeur de `x` (ou 10 si x=0)
- `6x` BAK: recule pointeur de `x` (ou 10 si x=0)
- `7` OUT: ecrit `chr(memory[memoryPointer])`
- `8` IN: lit 1 caractere d'entree et ecrit `ord(char) % 256`
- `9` RND: affecte une valeur aleatoire `0..255`

### 3.5 Gestion des erreurs

Messages d'erreur emis:

- `Program file not found: ...`
- `Input file not found: ...`
- `Unexpected EOF`
- `Missing argument`
- `Mismatched IF/EIF`

Les erreurs passent par `error(...)`:

- ecriture sur STDERR
- sortie non-zero (`sys.exit(1)`)

## 4) Outils (`tools/`)

## 4.1 `tools/tokenize.py`

Objectif:

- Afficher les tokens produits par les memes regles que `poetic.py`

Usage:

```powershell
python tools\tokenize.py examples\hello.ptc
python tools\tokenize.py -w examples\print_A.ptc
```

Sortie type:

- `TOKENS: [...]`

## 4.2 `tools/simulate.py`

Objectif:

- Tokeniser puis simuler pas a pas
- Afficher trace complete (IP, token, instruction, argument, pointeur memoire, fenetre memoire)

Options principales:

- `--tokens`: affiche tokens puis sort
- `--simulate`: execute la simulation
- `--step`: pause a chaque instruction
- `--max-steps N`: limite le nombre d'etapes
- `--delay S`: delai entre etapes
- `-w`: wimpmode

Exemples:

```powershell
python tools\simulate.py -w --tokens examples\print_A.ptc
python tools\simulate.py -w --simulate examples\print_A.ptc
python tools\simulate.py -w --simulate --step examples\print_A.ptc
```

Note:

- Pour `IN (8)`, la simulation ne lit pas STDIN et force EOF pour eviter le blocage.

## 4.3 `tools/simulate_text.py`

Objectif:

- Simuler depuis texte direct (`--text`) ou fichier
- Supporte accents latins de base via regex unicode

Options principales:

- `--text "..."`: source inline
- `file` optionnel: chemin fichier source
- `--tokens`
- `--simulate`
- `--step`
- `--delay`
- `-w`

Exemples:

```powershell
python tools\simulate_text.py --text "bonjour le monde" --tokens
python tools\simulate_text.py --text "bonjour le monde" --simulate
python tools\simulate_text.py examples\print_A.ptc -w --simulate
```

## 5) Exemples (`examples/`)

Fichiers presents:

- `hello.ptc`
- `bonjour.ptc`
- `cat.ptc`
- `tupni.ptc`
- `asciiloop.ptc`
- `random.ptc`
- `print_A.ptc`
- `print_bang.ptc`

Usages typiques:

```powershell
python poetic.py examples\hello.ptc
python poetic.py -w examples\bonjour.ptc
python poetic.py examples\cat.ptc
```

## 6) Tests (`tests/run_tests.py`)

Le script lance deux verifications end-to-end:

1. `hello.ptc` (mode normal)
   - attendu: `Hello World!`
2. `bonjour.ptc` (mode wimpmode)
   - attendu: `bonjour!`

Execution:

```powershell
python tests\run_tests.py
```

Codes de sortie:

- `0`: succes
- `1`: sortie inattendue
- `2`: erreur d'execution (retour non-zero)

## 7) Details importants et limitations

- Un mot de longueur 10 produit `0` (END si token isole), donc peut terminer un programme involontairement.
- Seuls les opcodes `3..6` acceptent des tokens a 2 chiffres.
- Les boucles IF/EIF supportent l'imbrication, mais une paire manquante provoque `Mismatched IF/EIF`.
- En mode simulation, le comportement de `IN` est simplifie (pas de lecture interactive selon l'outil).

## 8) Commandes rapides

Tokeniser:

```powershell
python tools\tokenize.py examples\hello.ptc
```

Executer:

```powershell
python poetic.py examples\hello.ptc
```

Executer en wimpmode:

```powershell
python poetic.py -w examples\print_A.ptc
```

Simuler avec trace:

```powershell
python tools\simulate.py --simulate examples\hello.ptc
```

Lancer les tests:

```powershell
python tests\run_tests.py
```
