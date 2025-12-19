#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file utils.py
@brief Fonctions utilitaires pour Planning Poker.
@details Ce module contient toutes les fonctions de calcul, parsing et vérification
utilisées par l'application Planning Poker GUI.

@author DJERDI Ilyas Kaci, SEDDIK Oussama
@version 1.0.0
@date Décembre 2025

@see config pour les constantes utilisées.
"""

from statistics import median, mean
from collections import Counter
import config


def parse_card_input(s):
    """
    @brief Parse l'entrée d'une carte.

    @details Convertit une chaîne de caractères en valeur de carte valide.
    Gère les cartes numériques (Fibonacci) et spéciales ("?", "coffee").

    @param s Chaîne d'entrée à parser (str, int, ou autre convertible en str).
    @return Valeur de la carte ou None si invalide.
    @retval int Pour les cartes numériques valides.
    @retval str "?" ou "coffee" pour les cartes spéciales.
    @retval None Si l'entrée n'est pas une carte valide.

    @par Exemple:
    @code
    parse_card_input("13")      # returns 13
    parse_card_input("?")       # returns "?"
    parse_card_input("coffee")  # returns "coffee"
    parse_card_input("invalid") # returns None
    @endcode

    @see config.CARDS pour les valeurs numériques acceptées.
    @see config.SPECIAL_CARDS pour les cartes spéciales acceptées.
    """
    s = str(s).strip()
    if s == "?":
        return "?"
    if s.lower() in ("coffee", "café", "cafe"):
        return "coffee"
    try:
        v = int(s)
        if v in config.CARDS:
            return v
    except ValueError:
        pass
    return None


def nearest_card_value(val):
    """
    @brief Trouve la valeur de carte la plus proche.

    @details Pour une valeur numérique donnée, trouve la carte Fibonacci
    dont la valeur est la plus proche (distance absolue minimale).
    Utilisé pour arrondir les résultats des moyennes et médianes.

    @param val Valeur numérique à comparer (int, float, ou convertible).
    @return Valeur de carte la plus proche ou None.

    @warning Retourne None si val est None ou non convertible en float.

    @par Exemple:
    @code
    nearest_card_value(7)   # returns 8
    nearest_card_value(10)  # returns 8
    nearest_card_value(25)  # returns 20
    @endcode

    @see config.CARDS pour la liste des valeurs disponibles.
    """
    if val is None:
        return None
    try:
        v = float(val)
    except Exception:
        return None
    diffs = [(abs(v - c), c) for c in config.CARDS]
    diffs.sort(key=lambda x: (x[0], x[1]))
    return diffs[0][1]


def majority_by_frequency(votes):
    """
    @brief Calcule la majorité par fréquence.

    @details Détermine la valeur numérique qui apparaît le plus souvent
    dans une liste de votes. Ignore les votes non numériques ("?", "coffee").
    En cas d'égalité de fréquence, retourne la valeur la plus élevée.

    @param votes Liste des votes (peut contenir int, "?", "coffee").
    @return Valeur numérique majoritaire ou None si pas de votes numériques.

    @note Ne considère que les votes de type int.

    @par Exemple:
    @code
    majority_by_frequency([5, 5, 8, 13])      # returns 5
    majority_by_frequency([8, 8, 5, 5])       # returns 8 (égalité, prend le plus grand)
    majority_by_frequency(["?", "coffee"])    # returns None
    @endcode
    """
    nums = [v for v in votes if isinstance(v, int)]
    if not nums:
        return None
    cnt = Counter(nums)
    most_common = cnt.most_common()
    highest_count = most_common[0][1]
    tied = [val for val, count in most_common if count == highest_count]
    return max(tied)


def percent_of_value(votes, value):
    """
    @brief Calcule le pourcentage d'une valeur dans les votes.

    @details Calcule le pourcentage de votes égaux à une valeur donnée.

    @param votes Liste des votes.
    @param value Valeur à compter dans les votes.
    @return Pourcentage (0.0 à 100.0) de la valeur dans la liste.

    @retval float Pourcentage entre 0.0 et 100.0.
    @retval 0.0 Si la liste de votes est vide.

    @par Exemple:
    @code
    percent_of_value([5, 5, 8, 13], 5)  # returns 50.0
    percent_of_value([], 5)             # returns 0.0
    @endcode
    """
    if not votes:
        return 0.0
    return votes.count(value) / len(votes) * 100.0


def all_coffee(votes):
    """
    @brief Vérifie si tous les votes sont 'coffee'.

    @details Teste si tous les éléments d'une liste de votes sont égaux à "coffee".
    Utilisé pour détecter une demande de pause collective.

    @param votes Liste des votes.
    @return True si tous les votes sont "coffee", False sinon.

    @note Retourne False si la liste est vide.

    @par Exemple:
    @code
    all_coffee(["coffee", "coffee", "coffee"])  # returns True
    all_coffee(["coffee", "?", "coffee"])       # returns False
    all_coffee([])                              # returns False
    @endcode
    """
    return len(votes) > 0 and all(v == "coffee" for v in votes)


def all_same(votes):
    """
    @brief Vérifie si tous les votes sont identiques.

    @details Teste si tous les éléments d'une liste de votes sont égaux.
    Utilisé pour détecter l'unanimité.

    @param votes Liste des votes.
    @return True si tous les votes sont identiques, False sinon.

    @note Retourne False si la liste est vide.

    @par Exemple:
    @code
    all_same([5, 5, 5, 5])    # returns True
    all_same(["?", "?", "?"]) # returns True
    all_same([5, 8, 5])       # returns False
    all_same([])              # returns False
    @endcode
    """
    return len(votes) > 0 and all(v == votes[0] for v in votes)