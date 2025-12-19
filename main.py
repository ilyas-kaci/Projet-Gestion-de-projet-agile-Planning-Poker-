#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file main.py
@brief Point d'entrée principal de l'application Planning Poker GUI.
@details Ce module initialise l'interface graphique Tkinter
et lance l'application principale.

@author DJERDI Ilyas Kaci, SEDDIK Oussama
@version 1.0.0
@date Décembre 2025

@see models.PlanningPokerGUI
@see config
@see utils
@see io_helpers
"""

import tkinter as tk
from models import PlanningPokerGUI


def main():
    """
    @brief Fonction principale de l'application.

    @details Crée la fenêtre principale Tkinter, instancie l'application
    PlanningPokerGUI, et démarre la boucle principale d'événements.

    @return None

    @note Cette fonction ne prend pas de paramètres et ne retourne rien.
    L'application se termine lorsque l'utilisateur ferme la fenêtre.

    @par Exemple d'utilisation:
    @code
    python main.py
    @endcode

    @see tk.Tk pour la création de la fenêtre principale.
    @see PlanningPokerGUI pour la classe principale de l'application.
    """
    root = tk.Tk()
    app = PlanningPokerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    """
    @brief Point d'entrée du script.

    @details Condition standard en Python pour exécuter la fonction main()
    uniquement lorsque le fichier est exécuté directement (pas importé).

    @par Pour lancer l'application:
    @code
    python main.py
    @endcode
    """
    main()