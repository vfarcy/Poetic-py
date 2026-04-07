Poetic (esolang) — interpréteur Python + site archivé

[![Site GitHub Pages](https://img.shields.io/badge/site-GitHub%20Pages-1f6feb)](https://vfarcy.github.io/Poetic-py/)

Références

- Internet Archive : https://web.archive.org/web/20210506130651/https://mcaweb.matc.edu/winslojr/vicom128/final/index.html
- Page Esolang : https://esolangs.org/wiki/Poetic_(esolang)

Vue d’ensemble

Ce dépôt contient :

- Un interpréteur Python pour Poetic : `poetic.py`
- Des exemples de programmes Poetic : `examples/*.ptc`
- Des utilitaires de tokenisation/simulation : `tools/`
- Une copie locale du site Poetic original : `site/`
- Un serveur local + API optionnels pour tests backend : `app.py` + `tools/serve_site.py`

Prérequis

- Python 3.10+ (fonctionne sur Windows PowerShell et terminaux standards)

Lancer l’interpréteur

Mode normal :

```powershell
python poetic.py examples\hello.ptc
```

Avec un fichier d’entrée :

```powershell
python poetic.py -i input.txt examples\cat.ptc
```

Wimpmode (source composée de chiffres) :

```powershell
python poetic.py -w examples\print_A.ptc
```

Règles du langage Poetic implémentées

- Le source est lu en UTF-8.
- Mode normal :
  - les caractères non alphabétiques deviennent des séparateurs (apostrophe supprimée),
  - chaque mot est remplacé par sa longueur,
  - la longueur 10 est encodée en `0`.
- Wimpmode (`-w`) : conserve uniquement les chiffres.
- Regex de tokenisation :

```python
re.findall(r"((?:[3456]\d)|\d)", program)
```

Instructions

- `0` END
- `1` IF
- `2` EIF
- `3x` INC x (`0` en argument signifie 10)
- `4x` DEC x (`0` en argument signifie 10)
- `5x` FWD x (`0` en argument signifie 10)
- `6x` BAK x (`0` en argument signifie 10)
- `7` OUT
- `8` IN
- `9` RND

Sémantique d’exécution

- Taille de bande mémoire : 30000 octets
- Valeurs d’octet en modulo 256
- Pointeur mémoire circulaire (wrap)
- IF/EIF supporte l’imbrication
- IN cesse de modifier la mémoire après EOF/CTRL+Z

Erreurs courantes de l’interpréteur

- `Unexpected EOF`
- `Missing argument`
- `Mismatched IF/EIF`

Utilitaires

- `tools/tokenize.py`
  - Affiche les tokens d’un fichier avec les mêmes règles que `poetic.py`
- `tools/simulate.py`
  - Simulation pas à pas avec trace d’exécution
- `tools/simulate_text.py`
  - Simulation depuis `--text` (pas besoin de fichier temporaire)

Exemples :

```powershell
python tools\tokenize.py examples\hello.ptc
python tools\simulate.py -w --simulate examples\print_A.ptc
python tools\simulate_text.py --text "bonjour le monde" --tokens
```

Site web (copie archivée) et Try It Online

Le dossier `site/` est une reconstruction locale du site original (pages, styles, polices, textures).

Depuis la version actuelle, la page TIO locale execute l'interpreteur Poetic directement dans le navigateur (client-side), comme l'archive d'origine.

Publication GitHub Pages

- Une GitHub Action est fournie dans `.github/workflows/deploy-pages.yml` pour publier directement le contenu de `site/` sur GitHub Pages.
- La publication se declenche sur chaque push vers `main` et peut aussi etre lancee manuellement depuis l'onglet Actions.
- Dans les reglages du depot GitHub, il faut definir la source GitHub Pages sur `GitHub Actions`.
- URL attendue du site publie : `https://vfarcy.github.io/Poetic-py/`
- URL attendue de la page TIO : `https://vfarcy.github.io/Poetic-py/tio/index.html`

Ouverture directe (sans serveur Python):

- Ouvrir `site/tio/index.html` dans le navigateur.

Serveur Python (optionnel)

Le serveur reste utile pour servir l'ensemble du site en HTTP et pour tester l'API backend.

Lancer le serveur web local + API :

```powershell
python app.py --port 8000
```

Puis ouvrir :

- Site principal : http://127.0.0.1:8000/
- Try It Online : http://127.0.0.1:8000/tio/index.html

Endpoint API backend (optionnel)

- `POST /api/run`
- Corps JSON :

```json
{
  "source": "...source poetic...",
  "input": "...texte stdin...",
  "wimpmode": false
}
```

- Réponse JSON (succès) :

```json
{
  "ok": true,
  "output": "...",
  "steps": 123,
  "tokens": 45
}
```

Notes sur la page TIO

- `Execute` lance le code Poetic dans le navigateur (sans appel API).
- `Stop` arrete l'execution locale.
- `Wimpmode OFF/ON` bascule le mode digits.
- `Share` génère un lien qui stocke source/input/wimpmode dans l’URL.
- L'indicateur affiche `Engine: Client-side`.

Structure du projet

- `poetic.py` — interpréteur CLI
- `app.py` — lanceur racine du serveur website (optionnel)
- `tools/poetic_engine.py` — runtime Poetic réutilisable pour scripts/API backend
- `tools/serve_site.py` — serveur HTTP + `/api/run` (optionnel)
- `site/` — pages/assets archivés (dont `site/tio/index.html`)
- `examples/` — exemples `.ptc`
- `tests/run_tests.py` — script de test

Depannage rapide

- Si le port 8000 est deja pris, utilise un autre port :

```powershell
python app.py --port 8011
```

- Puis ouvre l'URL correspondante (`http://127.0.0.1:8011/tio/index.html`).
