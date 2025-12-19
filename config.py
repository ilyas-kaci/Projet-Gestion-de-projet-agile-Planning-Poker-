#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file config.py
@brief Configuration et constantes pour Planning Poker GUI.
@details Ce module contient toutes les constantes globales utilisées dans l'application,
y compris les valeurs des cartes, les délais de pause, et les couleurs.

@author DJERDI Ilyas Kaci, SEDDIK Oussama
@version 1.0.0
@date Décembre 2025

@note Les cartes suivent la séquence de Fibonacci modifiée.
"""

# --- Config ---
CARDS = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100]
"""@var Liste des valeurs numériques des cartes Fibonacci."""

SPECIAL_CARDS = ["?", "coffee"]
"""@var Liste des cartes spéciales (non numériques)."""

ALL_CARDS = CARDS + SPECIAL_CARDS  # numeric ints + special strings
"""@var Liste de toutes les cartes disponibles (numériques + spéciales)."""

PAUSE_SECONDS = 5 * 60
"""@var Durée de la pause café en secondes."""

MAX_UNANIM_ATTEMPTS = 3
"""@var Nombre maximum de tentatives pour atteindre l'unanimité."""

# Couleurs des cartes
CARD_COLORS = {
    "?": "#87CEFA",
    "coffee": "#FFD700",
}
"""@var Dictionnaire des couleurs associées à chaque carte."""

# Génération des couleurs pour les cartes numériques
for i, c in enumerate(CARDS):
    lvl = 240 - int(i * (180 / max(1, len(CARDS) - 1)))
    CARD_COLORS[c] = f"#{int(lvl):02x}{int(255 - lvl / 2):02x}{int(200 - lvl / 3):02x}"

# Mapping des modes
MODES_MAP = {2: "mean", 3: "median", 4: "absolute", 5: "relative"}
"""@var Dictionnaire de correspondance entre codes numériques et noms de modes."""