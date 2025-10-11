Poetic (esolang) - petit interpréteur Python

But du projet

Ce dépôt contient une implémentation simple en Python d'un interpréteur pour le langage esoterique "Poetic".

Fichiers principaux

- `poetic.py` : l'interpréteur.
- `*.ptc` : exemples de programmes Poetic (ex. `hello.ptc`, `asciiloop.ptc`).

Comment exécuter

Utilisez votre interpréteur Python pour lancer `poetic.py` en passant le fichier `.ptc` en argument :

```powershell
python poetic.py hello.ptc
```

Test minimal

Un test minimal est fourni dans `tests/run_tests.py`. Il exécute `poetic.py` sur `hello.ptc` et vérifie que la sortie correspond à "Hello World!".

```powershell
python tests\run_tests.py
```

Prochaines améliorations possibles

- Ajouter un jeu de tests plus complet (pytest).
- Ajouter un linter/formatteur (flake8, black) et un CI.
- Ajouter gestion d'encoding/erreurs plus robuste et une couverture des exemples fournis.
