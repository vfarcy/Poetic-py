# Presentation du langage Bespokelang

**Bespokelang** est un langage esoterique fonde sur l'encodage par longueur de mots,
dans l'esprit de Poetic, mais avec un modele d'execution plus riche:

- pile (stack)
- tas associatif (heap)
- entiers en precision arbitraire
- controle structure (if/while/dowhile/function)

## 1) Modele de donnees

Le runtime manipule:

- **Stack**: pile principale (LIFO), operations de manipulation et d'arithmetique
- **Heap**: dictionnaire `adresse -> valeur` sur entiers
- **Functions**: table `nom -> bloc AST` definie par `CONTROL FUNCTION`
- **Input/Output**: flux texte en entree, sortie texte

Contrairement a Poetic, il n'y a pas de ruban 8-bit de taille fixe.

## 2) Encodage du source

Le code source est converti en chiffres via la longueur des mots:

- longueur `< 10` -> chiffre identique
- longueur `10` -> chiffre `0`
- longueur `> 10` -> plusieurs chiffres (ex: 12 -> `1`, `2`)

Details implementation:

- normalisation Unicode NFKC
- apostrophes acceptees dans les mots sans compter comme lettres
- les autres caracteres servent de separateurs

## 3) Categories d'instructions (0 a 9)

| Categorie | Nom | Role |
| :--- | :--- | :--- |
| `0` | COMMENTARY | Commentaires delimites par une signature `0...0` |
| `1` | H | Acces heap (load/store) |
| `2` | DO | Manipulation de pile |
| `3` | PUT | Push d'un litteral numerique multi-chiffres |
| `4` | PUSH | Push d'un chiffre simple |
| `5` | INPUT | Lecture nombre ou caractere |
| `6` | OUTPUT | Ecriture nombre ou caractere |
| `7` | CONTROL | Blocs et controle de flux |
| `8` | STACKTOP | Operations logiques/arithmetiques |
| `9` | CONTINUED | Extension d'un litteral ou nom de fonction |

## 4) Controle de flux

Sous-operations principales de `CONTROL`:

- `IF` (+ `OTHERWISE` optionnel + `END`)
- `WHILE ... END`
- `DOWHILE ... END`
- `FUNCTION <name> ... END`
- `CALL <name>`
- `BREAK`
- `RETURN`
- `ENDPROGRAM`

Le parseur construit un AST de blocs imbriques, puis l'interpreteur execute les blocs.

## 5) Calcul et semantique numerique

`STACKTOP` couvre notamment:

- negation logique (`F`)
- comparaison (`LT`)
- puissance/racine entiere (`POW` avec exposant negatif)
- `PLUS`, `MINUS`, `PRODUCTOF`, `QUOTIENTOF`, `MODULO`
- increments/decrements unitaires

Les calculs sont faits sur entiers Python natifs (precision arbitraire).

## 6) Entree / sortie

- `INPUT N`: lit un entier signe
- `INPUT CH`: lit un caractere, pousse son codepoint, ou `-1` en EOF
- `OUTPUT N`: ecrit le sommet de pile en decimal
- `OUTPUT CH`: ecrit le caractere Unicode correspondant (modulo l'espace codepoint)

## 7) Extensions de litteraux et commentaires

- `PUT` et certains `CONTROL` utilisent des nombres de taille variable.
- `CONTINUED` concatene des segments numeriques pour former:
  - un entier long (`PUT`)
  - un nom de fonction long (`FUNCTION`/`CALL`)
- `COMMENTARY` ignore un bloc de chiffres jusqu'a la signature de fermeture.

## 8) Positionnement

Bespokelang garde la dimension litteraire du code source, mais cible une execution
plus expressive et plus structuree que Poetic. Il est adapte a:

- experimentation sur les esolangs
- generation de prose executable
- demos d'interpreteur stack-based avec AST
