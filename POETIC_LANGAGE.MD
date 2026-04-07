# Présentation du langage Poetic

**Poetic** est un langage de programmation ésotérique fondé sur le fonctionnement du **Brainfuck**. Sa particularité réside dans l'utilisation du langage naturel comme code source, permettant de dissimuler des instructions informatiques au sein de textes littéraires ou poétiques.

## Architecture de données
Le système repose sur deux éléments principaux :
* **Le ruban (tape) :** Un ensemble de 30 000 cellules mémoires. Chaque cellule stocke un octet non signé (valeur comprise entre 0 et 255).
* **Le pointeur :** Un index mobile qui identifie la cellule mémoire en cours d'utilisation. Le ruban et les valeurs sont circulaires : un dépassement de la valeur 255 revient à 0, et un déplacement au-delà de la dernière cellule ramène à la première.

---

## Mécanisme de traduction
Le code source est interprété en comptant le nombre de lettres de chaque mot (les caractères non alphabétiques et les chiffres sont ignorés). 

| Longueur du mot ($n$) | Valeur numérique générée |
| :--- | :--- |
| $n < 10$ | Le chiffre $n$ |
| $n = 10$ | Le chiffre $0$ |
| $n > 10$ | Deux chiffres consécutifs (ex: 12 lettres → 1, 2) |

---

## Jeu d'instructions
Le langage comporte 10 instructions fondamentales déclenchées par les chiffres obtenus. Certaines commandes utilisent le chiffre généré par le mot suivant comme paramètre de donnée.

| Chiffre | Opcode | Description fonctionnelle |
| :--- | :--- | :--- |
| **1** | **IF** | Saute après le `EIF` correspondant si la cellule actuelle est égale à 0. |
| **2** | **EIF** | Retourne avant le `IF` correspondant si la cellule actuelle est différente de 0. |
| **3** | **INC** | Augmente la valeur de la cellule (le mot suivant définit la quantité). |
| **4** | **DEC** | Diminue la valeur de la cellule (le mot suivant définit la quantité). |
| **5** | **FWD** | Avance le pointeur mémoire (le mot suivant définit la distance). |
| **6** | **BAK** | Recule le pointeur mémoire (le mot suivant définit la distance). |
| **7** | **OUT** | Affiche la valeur de la cellule au format ASCII. |
| **8** | **IN** | Lit un caractère en entrée et stocke sa valeur ASCII dans la cellule. |
| **9** | **RND** | Assigne une valeur aléatoire (0-255) à la cellule actuelle. |
| **0** | **END** | Termine l'exécution du programme (sauf si utilisé comme donnée). |

---

## Philosophie du langage
L'objectif de Poetic est de permettre une double lecture du code : une lecture humaine, où le texte peut prendre la forme d'un poème ou d'un récit, et une lecture machine, strictement déterminée par la structure quantitative des mots. Cette dualité favorise l'obfuscation (dissimulation du code) et la recherche esthétique dans la programmation.