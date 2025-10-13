Poetic (esolang) — documentation

But du projet

Ce dépôt contient une implémentation simple en Python d'un interpréteur pour l'esolang "Poetic".

Fichiers principaux

- `poetic.py` : l'interpréteur.
- `*.ptc` : exemples de programmes Poetic (ex. `hello.ptc`, `asciiloop.ptc`).

Comment fonctionne le parsing (comment le texte devient des instructions)

- Mode normal (par défaut) :
	- Le fichier source est lu en UTF‑8.
	- On remplace chaque caractère non alphabétique par un espace (sauf l'apostrophe `'` qui est supprimée).
	- Le texte résultant est découpé en mots (split).
	- Chaque mot est remplacé par sa longueur (nombre de lettres). Si la longueur est 10, on utilise le chiffre `0` comme représentation (donc 10 → `0`).
	- On obtient une chaîne de chiffres (ex : longueurs de mots → "35370...").
	- Ensuite on applique l'expression régulière `re.findall(r"((?:[3456]\d)|\d)", program)` pour former les tokens :
		- On capture soit un token à deux chiffres dont le premier est 3,4,5 ou 6 (ex. `35`, `40`, `69`) — utile pour les instructions qui prennent un argument, soit un seul chiffre (`\d`) pour toutes les autres instructions.

- Mode wimpmode (`-w` / `--wimpmode`) :
	- On ne garde que les caractères numériques du fichier. Le reste est ignoré.
	- La même regex ci‑dessus est ensuite appliquée pour former la liste des tokens.

Remarque sur `0` :

- Lorsqu’un token `30`, `31`, ... ou `39` est capturé, le second caractère est l'argument. Si cet argument est `0`, il sera traité comme `10` (règle : argument `0` → valeur 10).
- Un token `0` isolé (capturé comme `\d`) est interprété comme instruction 0 (END).

Format des tokens et arguments

- Chaque élément du tableau `program` est une chaîne de longueur 1 (ex: `'7'`) ou 2 (ex: `'35'`).
- Pour chaque élément :
	- `currentInstruction = program[i][0]` — caractère de l'instruction.
	- Si possible `currentArgument = int(program[i][1])`. Si l'argument vaut `0`, il est converti en `10`.
- Seules les instructions `3`, `4`, `5`, `6` exigent un argument (sinon on déclenche `Missing argument`).

Architecture mémoire et conventions

- Mémoire : `memory = bytearray(30000)` — tableau de 30 000 octets initialisés à 0 (similaire à Brainfuck).
- `memoryPointer` est en 0..29999 ; les déplacements utilisent `mod len(memory)` (wrap-around).
- Les octets sont traités modulo 256 (opérations INC/DEC font `% 256`).
- EOF input handling : si on rencontre EOF ou CTRL+Z (valeur 26), la lecture met `eofReached = True` et les instructions `IN` ultérieures ne modifient pas la mémoire.

Instructions (0–9)

0 — END
	- Effet : termine l'exécution (sortie immédiate de la boucle principale).
	- Note : si `0` apparaît comme argument (par ex. dans token `30`) il est d'abord converti en 10 avant usage — donc `30` signifie INC de 10.

1 — IF
	- Syntaxe : `1`.
	- Effet : si la case mémoire courante est égale à 0, saute l'exécution jusqu'après le `EIF` correspondant (gestion de la profondeur imbriquée).
	- Erreur : `Mismatched IF/EIF` si on ne trouve pas d'EIF.

2 — EIF
	- Syntaxe : `2`.
	- Effet : si la case mémoire courante ≠ 0, saute en arrière jusqu'avant le `IF` correspondant (boucle).
	- Erreur : `Mismatched IF/EIF` si on ne trouve pas d'IF.

3 — INC
	- Syntaxe : token à 2 caractères dont le premier est `3` (ex. `35`).
	- Argument : deuxième chiffre (0..9) ; si argument == 0 alors valeur utilisée = 10.
	- Effet : `memory[pointer] = (memory[pointer] + argument) % 256`.
	- Erreur : `Missing argument` si absent.

4 — DEC
	- Syntaxe : token commençant par `4` (ex. `42`).
	- Argument : second chiffre, 0→10.
	- Effet : `memory[pointer] = (memory[pointer] - argument) % 256`.
	- Erreur : `Missing argument` si absent.

5 — FWD
	- Syntaxe : token commençant par `5` (ex. `51`).
	- Argument : second chiffre, 0→10.
	- Effet : `memoryPointer = (memoryPointer + argument) % len(memory)`.
	- Erreur : `Missing argument` si absent.

6 — BAK
	- Syntaxe : token commençant par `6` (ex. `63`).
	- Argument : second chiffre, 0→10.
	- Effet : `memoryPointer = (memoryPointer - argument) % len(memory)`.
	- Erreur : `Missing argument` si absent.

7 — OUT
	- Syntaxe : `7`.
	- Effet : affiche le caractère ASCII représenté par l'octet courant (`print(chr(memory[memoryPointer]), end="", flush=True)`).

8 — IN
	- Syntaxe : `8`.
	- Effet : lit 1 caractère depuis `inputStream.read(1)` et stocke `ord(char) % 256` dans la case courante.
	- Si on lit CTRL+Z (26), le code marque `eofReached = True`.
	- Si EOF atteint, l'instruction IN ne modifie pas la mémoire.

9 — RND
	- Syntaxe : `9`.
	- Effet : `memory[memoryPointer] = random.randint(0,255)`.

Erreurs et messages gérés

- `Unexpected EOF` : on a dépassé la fin du tableau `program` sans rencontrer un `0` (END).
- `Missing argument` : instruction `3`/`4`/`5`/`6` sans argument.
- `Mismatched IF/EIF` : pas d'IF correspondant lors du saut avant/arrière.
- Tous les `error(...)` écrivent sur STDERR et appellent `sys.exit()` (amélioration recommandée : utiliser `sys.exit(1)`).

Subtilités importantes

- Seuls `3`..`6` peuvent former des tokens à deux chiffres (instruction + argument). D'où la regex qui attrape deux chiffres seulement si le premier est 3–6.
- L'argument `0` dans une instruction à argument est interprété comme `10`.
- Les déplacements et valeurs sont circulaires (pointer modulo taille mémoire, bytes modulo 256).
- `inputStream` : si l'option `-i/--input` est fournie, le fichier est ouvert (actuellement sans encoding explicite dans le code pour l'input) ; sinon on utilise STDIN.

Exemples rapides

- Exécuter le programme `hello.ptc` :

```powershell
python poetic.py hello.ptc
```

- Mode wimpmode (le fichier contient directement des chiffres) :

```powershell
python poetic.py -w program_with_digits.ptc
```

Écrire un petit poème → tokenisation (exemple simplifié)

- Texte : "love is a great mystery"
- Étapes : on retire les caractères non-alfabétiques → mots = ["love","is","a","great","mystery"]
- longueurs = [4,2,1,5,7] → chiffres concaténés = "42157"
- Appliquer la regex de tokens : `['4','2','1','5','7']` → instructions : DEC 2, IF, END/..., etc. (ceci est un exemple pédagogique : le résultat réel dépend de la suite entière du texte)

Recommandations (améliorations rapides)

1. Rendre `error()` explicite : `sys.exit(1)` pour les erreurs.
2. Ouvrir les fichiers avec gestion d'erreur (`try/except`) et utiliser `with open(...):` pour fermer automatiquement.
3. Ajouter des tests unitaires (pytest) pour couvrir les erreurs `Missing argument` et `Mismatched IF/EIF` ainsi que des cas de bord.
4. Ajouter un linter/formatteur (black + flake8) et configurer un CI (ex: GitHub Actions) si le projet évolue.

Fichiers utiles fournis

- `hello.ptc` — exemple qui affiche "Hello World!".
- `tests/run_tests.py` — test minimal qui exécute `poetic.py` sur `hello.ptc` et vérifie la sortie.

Souhaitez-vous que j'applique automatiquement les corrections non intrusives listées (Option A) ?

Utilitaire : `tools/tokenize.py`

Un petit utilitaire `tools/tokenize.py` a été ajouté pour afficher les tokens extraits d'un fichier `.ptc` en reprenant exactement les règles de parsing de `poetic.py` (mode normal et `-w`). Ceci est utile pour déboguer ou construire des programmes Poetic de manière fiable.

Usage :

- Tokenize en mode normal (texte → longueurs → tokens) :

```powershell
python tools\tokenize.py hello.ptc
```

- Tokenize en mode wimpmode (garde seulement les chiffres) :

```powershell
python tools\tokenize.py -w examples\print_A.ptc
```

Exemples ajoutés dans le dépôt :

- `examples/print_A.ptc` — impressions de 'A' (utiliser `-w`) ; se termine par `0` (END).
- `examples/print_bang.ptc` — impressions de '!' (utiliser `-w`) ; se termine par `0` (END).

Ces outils et exemples facilitent la construction et la vérification manuelle de petits programmes Poetic.

Utilities détaillées

- `tools/tokenize.py`
	- Objectif : afficher la liste des tokens extraits d'un fichier `.ptc` en utilisant exactement le même parser que `poetic.py` (mode normal ou `-w`).
	- Usage :
		- Mode normal (texte → longueurs → tokens) :
			```powershell
			python tools\tokenize.py hello.ptc
			```
		- Mode wimpmode (garde seulement les chiffres) :
			```powershell
			python tools\tokenize.py -w examples\print_A.ptc
			```

- `tools/simulate.py`
	- Objectif : tokeniser puis simuler l'exécution des tokens en affichant un trace pas-à-pas (dump d'état avant chaque instruction). Permet de visualiser IP, token courant, instruction, argument, pointeur mémoire et fenêtre mémoire.
	- Options utiles :
		- `--tokens` : affiche uniquement les tokens et sort.
		- `--simulate` : exécute la simulation et affiche la trace.
		- `--step` : mode interactif, attend Enter entre chaque instruction pour avancer.
		- `--delay N` : ajoute N secondes d'attente entre chaque instruction quand on n'est pas en mode step.
	- Exemples :
		- Voir les tokens :
			```powershell
			python tools\simulate.py -w --tokens examples\print_A.ptc
			```
		- Simuler avec trace :
			```powershell
			python tools\simulate.py -w --simulate examples\print_A.ptc
			```
		- Mode pas-à-pas :
			```powershell
			python tools\simulate.py -w --simulate --step examples\print_A.ptc
			```

Notes

- Les deux utilitaires reprennent fidèlement le comportement du parser de `poetic.py` : en mode normal les mots sont convertis en longueurs (10 → `0`), en `-w` on ne garde que les chiffres.
- `tools/simulate.py` n'essaie pas de lire de l'entrée interactive pour l'instruction `IN` (8) durant la simulation : il marque l'EOF pour la simulation. C'est volontaire pour éviter le blocage lors d'une simulation non interactive.


Comportement des mots de longueur > 10

- Règle générale : chaque mot est remplacé par sa longueur (p. ex. 11 → "11"). Le seul cas spécial déjà codé est 10 → "0".
- Conséquence : un mot de longueur 11 produit la chaîne "11" qui sera découpée par la regex en tokens `['1','1']` (donc deux instructions `1`, `1`).
- Exemples :
	- longueur 9 → token `['9']` (RND)
	- longueur 10 → token `['0']` (END)  ← attention : termine le programme
	- longueur 11 → tokens `['1','1']` → IF, IF
	- longueur 12 → tokens `['1','2']` → IF, EIF
	- longueur 35 → tokens `['35']` → INC 5 (puisque 3x peut former un token à deux chiffres)
	- longueur 103 → tokens `['1','0','3']` → IF, END, OUT (comportement potentiellement surprenant)

- Points clés à garder en tête :
	- Seule la longueur 10 est compressée en '0' par le parsing initial ; les autres longueurs >9 restent multi-chiffres.
	- Les tokens sont extraits ensuite selon la règle "deux chiffres si premier chiffre est 3–6, sinon un chiffre" — donc la découpe dépend fortement de l'alignement des chiffres.
	- Un `0` isolé (idéalement issu d'une longueur 10) provoquera un `END` immédiat.

Recommandations pratiques

- Évitez les mots de longueur exactement 10 sauf si vous voulez explicitement terminer le programme.
- Évitez de compter sur des longueurs > 9 pour générer des arguments multi-chiffres : préférez plusieurs instructions (ex : `30` pour INC 10 ou `35` puis `35` pour INC 5 deux fois) ou utilisez le mode `-w` et mettez les chiffres explicitement.
- Si vous le souhaitez, je peux modifier le parser pour émettre des avertissements lors de la détection d'un `0` isolé (longueur 10) ou pour supporter un encodage différent des longueurs > 9 (ex : mapping modulo 10 ou scindage contrôlé).

`tools/simulate_text.py` — simulation depuis du texte

Un utilitaire `tools/simulate_text.py` a été ajouté pour tokeniser et simuler directement à partir d'une chaîne de texte fournie avec `--text` (ou à partir d'un fichier). Il reprend les mêmes règles que `poetic.py` mais permet de travailler sans créer de fichier `.ptc` intermédiaire.

Exemples rapides :

```powershell
python tools\simulate_text.py --text "bonjour le monde" --tokens
python tools\simulate_text.py --text "bonjour le monde" --simulate
python tools\simulate_text.py examples\print_A.ptc -w --simulate
```

Notes Unicode : le script utilise une approche portable (plage Unicode Latin de base) pour préserver les lettres accentuées françaises. Pour une couverture Unicode complète on peut remplacer l'expression régulière par la bibliothèque tierce `regex` et utiliser `\p{L}`.

Contribuer

- Si vous voulez que j'ouvre une Pull Request depuis `test-branch` vers `main`, dites-le et je la créerai.
- Suggestions rapides : ajouter `pytest` + quelques tests unitaires, ajouter un workflow GitHub Actions pour lancer les tests automatiquement, ou améliorer la gestion Unicode en utilisant `regex`.

