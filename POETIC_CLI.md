# MANUAL - Poetic-py (source: origin/main)

Ce document decrit le fonctionnement de ```poetic.py```.

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

## 9) Annexe detaillee (parsing, ISA, erreurs)

### 9.1 Comment fonctionne le parsing (comment le texte devient des instructions)

Mode normal (par defaut):

1. Le fichier source est lu en UTF-8.
2. On remplace chaque caractere non alphabetique par un espace (sauf l'apostrophe `'` qui est supprimee).
3. Le texte resultant est decoupe en mots (`split`).
4. Chaque mot est remplace par sa longueur (nombre de lettres). Si la longueur est 10, on utilise le chiffre `0` comme representation (donc 10 -> 0).
5. On obtient une chaine de chiffres (ex: longueurs de mots -> `"35370..."`).
6. Ensuite on applique l'expression reguliere `re.findall(r"((?:[3456]\d)|\d)", program)` pour former les tokens:
    - On capture soit un token a deux chiffres dont le premier est 3, 4, 5 ou 6 (ex: `35`, `40`, `69`) utile pour les instructions qui prennent un argument.
    - Soit un seul chiffre (`\d`) pour toutes les autres instructions.

Mode wimpmode (`-w` / `--wimpmode`):

1. On ne garde que les caracteres numeriques du fichier. Le reste est ignore.
2. La meme regex ci-dessus est ensuite appliquee pour former la liste des tokens.

Remarque sur `0`:

- Lorsqu'un token `30`, `31`, ... ou `39` est capture, le second caractere est l'argument. Si cet argument est `0`, il sera traite comme `10` (regle: argument `0` -> valeur `10`).
- Un token `0` isole (capture comme `\d`) est interprete comme instruction `0` (END).

### 9.2 Format des tokens et arguments

- Chaque element du tableau `program` est une chaine de longueur 1 (ex: `'7'`) ou 2 (ex: `'35'`).
- Pour chaque element:
   - `currentInstruction = program[i][0]` -> caractere de l'instruction.
   - Si possible `currentArgument = int(program[i][1])`. Si l'argument vaut `0`, il est converti en `10`.
- Seules les instructions `3`, `4`, `5`, `6` exigent un argument (sinon on declenche `Missing argument`).

### 9.3 Architecture memoire et conventions

- Memoire: `memory = bytearray(30000)` -> tableau de 30 000 octets initialises a 0 (similaire a Brainfuck).
- `memoryPointer` est en 0..29999; les deplacements utilisent `mod len(memory)` (wrap-around).
- Les octets sont traites modulo 256 (operations INC/DEC font `% 256`).
- EOF input handling: si on rencontre EOF ou CTRL+Z (valeur 26), la lecture met `eofReached = True` et les instructions IN ulterieures ne modifient pas la memoire.

### 9.4 Instructions (0-9)

`0` - END

- Effet: termine l'execution (sortie immediate de la boucle principale).
- Note: si `0` apparait comme argument (par ex. dans token `30`) il est d'abord converti en `10` avant usage, donc `30` signifie INC de 10.

`1` - IF

- Syntaxe: `1`.
- Effet: si la case memoire courante est egale a 0, saute l'execution jusqu'apres le EIF correspondant (gestion de la profondeur imbriquee).
- Erreur: `Mismatched IF/EIF` si on ne trouve pas d'EIF.

`2` - EIF

- Syntaxe: `2`.
- Effet: si la case memoire courante n'est pas egale a 0, saute en arriere jusqu'avant le IF correspondant (boucle).
- Erreur: `Mismatched IF/EIF` si on ne trouve pas d'IF.

`3` - INC

- Syntaxe: token a 2 caracteres dont le premier est `3` (ex. `35`).
- Argument: deuxieme chiffre (0..9); si argument == 0 alors valeur utilisee = 10.
- Effet: `memory[pointer] = (memory[pointer] + argument) % 256`.
- Erreur: `Missing argument` si absent.

`4` - DEC

- Syntaxe: token commencant par `4` (ex. `42`).
- Argument: second chiffre, 0->10.
- Effet: `memory[pointer] = (memory[pointer] - argument) % 256`.
- Erreur: `Missing argument` si absent.

`5` - FWD

- Syntaxe: token commencant par `5` (ex. `51`).
- Argument: second chiffre, 0->10.
- Effet: `memoryPointer = (memoryPointer + argument) % len(memory)`.
- Erreur: `Missing argument` si absent.

`6` - BAK

- Syntaxe: token commencant par `6` (ex. `63`).
- Argument: second chiffre, 0->10.
- Effet: `memoryPointer = (memoryPointer - argument) % len(memory)`.
- Erreur: `Missing argument` si absent.

`7` - OUT

- Syntaxe: `7`.
- Effet: affiche le caractere ASCII represente par l'octet courant (`print(chr(memory[memoryPointer]), end="", flush=True)`).

`8` - IN

- Syntaxe: `8`.
- Effet: lit 1 caractere depuis `inputStream.read(1)` et stocke `ord(char) % 256` dans la case courante.
- Si on lit CTRL+Z (26), le code marque `eofReached = True`.
- Si EOF atteint, l'instruction IN ne modifie pas la memoire.

`9` - RND

- Syntaxe: `9`.
- Effet: `memory[memoryPointer] = random.randint(0,255)`.

### 9.5 Erreurs et messages geres

- `Unexpected EOF`: on a depasse la fin du tableau `program` sans rencontrer un `0` (END).
- `Missing argument`: instruction `3`/`4`/`5`/`6` sans argument.
- `Mismatched IF/EIF`: pas d'IF correspondant lors du saut avant/arriere.
- Tous les `error(...)` ecrivent sur STDERR et appellent `sys.exit(1)`.

### 9.6 Subtilites importantes

- Seuls `3..6` peuvent former des tokens a deux chiffres (instruction + argument). D'ou la regex qui attrape deux chiffres seulement si le premier est 3-6.
- L'argument `0` dans une instruction a argument est interprete comme `10`.
- Les deplacements et valeurs sont circulaires (pointer modulo taille memoire, bytes modulo 256).
- `inputStream`: si l'option `-i/--input` est fournie, le fichier est ouvert; sinon on utilise STDIN.

### 9.7 Exemples rapides

Executer le programme `hello.ptc`:

```powershell
python poetic.py hello.ptc
```

Mode wimpmode (le fichier contient directement des chiffres):

```powershell
python poetic.py -w program_with_digits.ptc
```

### 9.8 Ecrire un petit poeme -> tokenisation (exemple simplifie)

- Texte: `"love is a great mystery"`
- Etapes: on retire les caracteres non-alphabetiques -> mots = `["love", "is", "a", "great", "mystery"]`
- Longueurs = `[4,2,1,5,7]` -> chiffres concat en `"42157"`
- Application de la regex de tokens: `['4','2','1','5','7']` -> instructions DEC 2, IF, END/..., etc. (exemple pedagogique, le resultat reel depend de la suite complete du texte)
