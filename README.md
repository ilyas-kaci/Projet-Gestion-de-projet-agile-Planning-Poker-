# Planning Poker GUI

[![Generate Doxygen Documentation](https://github.com/ilyas-kaci/Projet-Gestion-de-projet-agile-Planning-Poker-/actions/workflows/doxygen.yml/badge.svg)](https://github.com/ilyas-kaci/Projet-Gestion-de-projet-agile-Planning-Poker-/actions/workflows/doxygen.yml)

Application de Planning Poker avec interface graphique Tkinter, documentation automatisée et intégration continue.

## Table des matières
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Intégration Continue](#-intégration-continue)
- [Auteurs](#-auteurs)

## Fonctionnalités

- ** Interface graphique intuitive** (Tkinter)
- ** Système de vote par cartes Fibonacci** (0, 1, 2, 3, 5, 8, 13, 20, 40, 100)
- ** Gestion des pauses café** avec sauvegarde automatique
- ** Sauvegarde/chargement** des parties au format JSON
- ** 5 modes de résolution** : Unanimité, Moyenne, Médiane, Majorité absolue/relative
- ** Documentation technique automatisée** avec Doxygen
- ** Intégration Continue** via GitHub Actions

## Installation

### Prérequis
- Python 3.8 ou supérieur
- Tkinter (généralement inclus avec Python)

### Installation depuis GitHub

# Cloner le dépôt
git clone https://github.com/ilyas-kaci/Projet-Gestion-de-projet-agile-Planning-Poker-.git

# Se déplacer dans le dossier
cd Projet-Gestion-de-projet-agile-Planning-Poker-

# Lancer l'application
python main.py

# Utilisation :

Démarrer une nouvelle partie : Cliquez sur "Nouvelle partie"

Configurer les joueurs : Saisissez le nombre et les noms des participants

Choisir le mode de vote : Sélectionnez parmi les 5 modes disponibles

Charger un backlog : Depuis un fichier JSON ou création manuelle

Voter : Cliquez sur les cartes pendant votre tour

Sauvegarder : Les parties peuvent être sauvegardées à tout moment

# Architecture :

Projet-Gestion-de-projet-agile-Planning-Poker-/
├── main.py              # Point d'entrée principal
├── models.py           # Classes principales (Task, PlanningPokerGUI)
├── utils.py            # Fonctions utilitaires (calculs, parsing)
├── io_helpers.py       # Gestion fichiers JSON et dialogues modaux
├── config.py           # Constantes et configuration globale
├── projet_ppgp.py      # Version originale (historique)
├── Doxyfile           # Configuration de la documentation
├── .github/workflows/ # Pipeline CI/CD
│   └── doxygen.yml    # Workflow de génération de documentation
└── docs/              # Documentation générée (automatique)

# Documentation :

# Documentation Technique :

La documentation de l'API est générée automatiquement avec Doxygen :
# Génération locale
sudo apt-get install doxygen graphviz
doxygen Doxyfile
# Ouvrir : docs/html/index.html

Documentation en ligne :

La documentation est générée automatiquement à chaque commit via GitHub Actions :

Artefact téléchargeable : Disponible dans l'onglet "Actions"

Couverture : Tous les modules, classes et fonctions publiques

# Intégration Continue
Pipeline GitHub Actions
À chaque push sur la branche main :

- Checkout du code

- Installation de Doxygen et Graphviz

- Génération de la documentation HTML

- Archivage en tant qu'artefact (doxygen-docs)

# Auteurs :
DJERDI Ilyas Kaci
SEDDIK Oussama
# Licence
Ce projet est réalisé dans le cadre d'un cours de gestion de projet agile.
Code source disponible pour référence académique.

