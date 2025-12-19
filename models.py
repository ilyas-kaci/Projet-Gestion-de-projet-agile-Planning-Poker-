#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file models.py
@brief Classes principales pour Planning Poker GUI.
@details Ce module contient les classes représentant les tâches et l'interface
graphique principale de l'application Planning Poker.

@author DJERDI Ilyas Kaci, SEDDIK Oussama
@version 1.0.0
@date Décembre 2025

@see config pour les constantes de configuration.
@see utils pour les fonctions utilitaires.
@see io_helpers pour la gestion des fichiers et dialogues.
"""

import time
import tkinter as tk
import config
import utils
import io_helpers


class Task:
    """
    @class Task
    @brief Classe représentant une tâche dans le backlog.

    @details Une tâche contient un identifiant, un titre, une description,
    une estimation finale et un historique des votes.

    @note Utilisée pour la sérialisation/désérialisation JSON.
    """

    def __init__(self, task_id, title, description=""):
        """
        @brief Constructeur de la classe Task.

        @param task_id Identifiant unique de la tâche.
        @param title Titre de la tâche.
        @param description Description détaillée de la tâche (optionnel).
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.estimation = None
        self.history = []

    def to_dict(self):
        """
        @brief Convertit la tâche en dictionnaire.

        @details Utilisé pour la sérialisation JSON.

        @return Dictionnaire représentant la tâche.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "estimation": self.estimation,
            "history": self.history.copy()
        }

    @classmethod
    def from_dict(cls, data):
        """
        @brief Crée une tâche à partir d'un dictionnaire.

        @details Méthode de classe pour désérialiser depuis JSON.

        @param data Dictionnaire contenant les données de la tâche.
        @return Instance de Task.
        """
        task = cls(
            task_id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", "")
        )
        task.estimation = data.get("estimation")
        task.history = data.get("history", [])
        return task


class PlanningPokerGUI:
    """
    @class PlanningPokerGUI
    @brief Classe principale de l'interface graphique.

    @details Gère toute l'interface utilisateur Tkinter, la logique de vote,
    et la communication entre les différents composants de l'application.

    @note Version vérifiée et fonctionnelle.
    """

    def __init__(self, root):
        """
        @brief Constructeur de PlanningPokerGUI.

        @param root Fenêtre racine Tkinter.
        """
        self.root = root
        root.title("Planning Poker (GUI complet)")

        # États du jeu (EXACTEMENT comme l'original)
        self.players = []
        self.backlog = []  # Gardé pour compatibilité
        self.state = []  # Liste d'objets Task
        self.mode_primary = "strict"
        self.mode_secondary = None

        # États de la partie en cours (EXACTEMENT comme l'original)
        self.current_task_index = 0
        self.attempt = 1
        self.current_player_index = 0
        self.votes_current_attempt = []
        self.history_tmp = []

        # Initialisation de l'interface (identique à l'original)
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur (identique à l'original)"""
        # Frames principales
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(padx=10, pady=6, anchor="w")

        self.ctrl_frame = tk.Frame(self.root)
        self.ctrl_frame.pack(fill="x", padx=10)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(padx=10, pady=10)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(fill="x", padx=10, pady=6)

        # Contrôles du haut
        tk.Button(self.top_frame, text="Nouvelle partie",
                  command=self.menu_new).pack(side="left", padx=4)
        tk.Button(self.top_frame, text="Reprendre partie",
                  command=self.menu_load).pack(side="left", padx=4)
        tk.Button(self.top_frame, text="Quitter",
                  command=self.root.quit).pack(side="left", padx=4)

        # Labels d'information
        self.task_label = tk.Label(self.ctrl_frame, text="Aucune partie lancée",
                                   font=("Arial", 14))
        self.task_label.pack(anchor="w")

        self.info_label = tk.Label(self.ctrl_frame, text="",
                                   font=("Arial", 10))
        self.info_label.pack(anchor="w")

        # Canvas pour les cartes
        self.cards_canvas = tk.Canvas(self.canvas_frame, width=1200,
                                      height=220, bg="#f6f6f6")
        self.cards_canvas.pack()

        # Bouton d'action
        self.next_button = tk.Button(self.bottom_frame, text="Suivant (tâche)",
                                     state="normal", command=self.next_task_manual)
        self.next_button.pack(side="right")

        # Items des cartes
        self.card_items = []

    # ---------- Menus ----------
    def menu_new(self):
        """Démarre une nouvelle partie - LOGIQUE IDENTIQUE À L'ORIGINAL"""
        # reset (identique)
        self.players = []
        self.backlog = []
        self.state = []
        self.mode_primary = "strict"
        self.mode_secondary = None
        self.current_task_index = 0
        self.attempt = 1
        self.current_player_index = 0
        self.votes_current_attempt = []
        self.history_tmp = []

        # players (identique)
        n = io_helpers.modal_askinteger(self.root, "Joueurs", "Nombre de joueurs (>=2) :")
        if n is None:
            return
        for i in range(n):
            name = io_helpers.modal_askstring(self.root, "Pseudo", f"Pseudo joueur {i + 1} :")
            self.players.append((name or f"Player{i + 1}").strip())

        # choose mode (identique)
        self.choose_mode_dialog()

        # backlog: load or manual (identique)
        choice = io_helpers.modal_askyesno(self.root, "Backlog",
                                           "Charger backlog depuis un fichier JSON ? (Oui = charger, Non = créer manuellement)")
        if choice:
            path = io_helpers.modal_askopenfilename(self.root,
                                                    title="Charger backlog JSON", filetypes=[("JSON files", "*.json")])
            if not path:
                io_helpers.modal_warning(self.root, "Annulé", "Chargement annulé.")
                return
            try:
                self.backlog = io_helpers.load_backlog_from_file(path)
            except Exception as e:
                io_helpers.modal_error(self.root, "Erreur", f"Impossible de charger le backlog : {e}")
                return
        else:
            m = io_helpers.modal_askinteger(self.root, "Tâches", "Combien de tâches ajouter ?")
            if m is None:
                return
            for i in range(m):
                t = io_helpers.modal_askstring(self.root, "Titre", f"Titre tâche {i + 1} :") or f"Tâche {i + 1}"
                desc = io_helpers.modal_askstring(self.root, "Description", "Description (optionnelle) :") or ""
                self.backlog.append({"id": f"t{i + 1}", "title": t, "description": desc})

        # build state (adapté pour utiliser Task)
        self.state = []
        for t in self.backlog:
            task = Task(
                task_id=t.get("id"),
                title=t.get("title"),
                description=t.get("description", "")
            )
            self.state.append(task)

        # start first task (identique)
        self.current_task_index = 0
        self.load_task()

    def menu_load(self):
        """Charge une partie sauvegardée - LOGIQUE IDENTIQUE À L'ORIGINAL"""
        path = io_helpers.modal_askopenfilename(self.root,
                                                title="Charger sauvegarde JSON", filetypes=[("JSON files", "*.json")])
        if not path:
            return

        try:
            saved = io_helpers.load_saved_state(path)
        except Exception as e:
            io_helpers.modal_error(self.root, "Erreur", f"Impossible de charger la sauvegarde : {e}")
            return

        # Restauration (identique)
        self.players = saved.get("players", [])
        mode = saved.get("mode", {})
        self.mode_primary = mode.get("primary", "strict")
        self.mode_secondary = mode.get("secondary", None)

        # Conversion en objets Task
        self.state = []
        state_data = saved.get("state", [])
        for s in state_data:
            task = Task(
                task_id=s.get("id"),
                title=s.get("title"),
                description=s.get("description", "")
            )
            task.estimation = s.get("estimation")
            task.history = s.get("history", [])
            self.state.append(task)

        # Reconstruction du backlog
        self.backlog = []
        for task in self.state:
            self.backlog.append({
                "id": task.id,
                "title": task.title,
                "description": task.description
            })

        # restore position (identique)
        self.current_task_index = saved.get("current_task_index", 0)
        self.attempt = 1
        self.current_player_index = 0
        self.votes_current_attempt = []
        self.history_tmp = []

        io_helpers.modal_info(self.root, "OK",
                              f"Partie chargée : {len(self.state)} tâches, joueurs = {self.players}")
        io_helpers.modal_info(self.root, "Reprise",
                              f"La partie reprendra à la tâche {self.current_task_index + 1}.")

        self.load_task()

    def choose_mode_dialog(self):
        """Dialogue de choix du mode - IDENTIQUE À L'ORIGINAL"""
        dlg = io_helpers.modal_askinteger(self.root, "Mode",
                                          "Choisissez le mode (1=Strict + option secondaire, 2=Moyenne, 3=Médiane, 4=Majorité absolue, 5=Majorité relative) :")

        if dlg is None:
            self.mode_secondary = None
            return

        if dlg == 1:
            v2 = io_helpers.modal_askinteger(self.root, "Second mode",
                                             "Second mode (0=aucun, 2=mean,3=median,4=absolute,5=relative) :")
            if v2 is None or v2 == 0:
                self.mode_secondary = None
            else:
                self.mode_secondary = config.MODES_MAP.get(v2)
        else:
            self.mode_secondary = config.MODES_MAP.get(dlg)

    # ---------- Gestion des tâches ----------
    def load_task(self):
        """Charge et affiche la tâche courante - IDENTIQUE À L'ORIGINAL"""
        if self.current_task_index >= len(self.state):
            self.save_final_results()
            return

        task = self.state[self.current_task_index]
        self.task_label.config(
            text=f"Tâche {self.current_task_index + 1}/{len(self.state)} : {task.title}")
        self.info_label.config(text=f"Description: {task.description}")

        # reset attempt counters (identique)
        self.attempt = 1
        self.current_player_index = 0
        self.votes_current_attempt = []
        self.history_tmp = []

        self.draw_cards()
        self.update_turn_label()

    def update_turn_label(self):
        """Met à jour le label du tour - IDENTIQUE À L'ORIGINAL"""
        if self.current_task_index < len(self.state):
            if not self.players:
                self.info_label.config(text="Aucun joueur défini.")
                return
            current_player = self.players[self.current_player_index % len(self.players)]
            self.info_label.config(
                text=f"Tâche: {self.state[self.current_task_index].title}    "
                     f"Tentative {self.attempt}/{config.MAX_UNANIM_ATTEMPTS} - "
                     f"Tour joueur: {current_player}")

    # ---------- Affichage des cartes ----------
    def draw_cards(self):
        """Dessine les cartes sur le canvas - IDENTIQUE À L'ORIGINAL"""
        self.cards_canvas.delete("all")
        self.card_items = []

        w, h = 70, 110
        margin, start_x, y0 = 12, 10, 20

        for i, val in enumerate(config.ALL_CARDS):
            x0 = start_x + i * (w + margin)
            x1 = x0 + w
            y1 = y0 + h

            display_val = str(val)
            color = config.CARD_COLORS.get(val, "#ffffff")

            rect = self.cards_canvas.create_rectangle(
                x0, y0, x1, y1, fill=color,
                outline="#333", width=2, tags=("card",)
            )

            text = self.cards_canvas.create_text(
                (x0 + x1) // 2, (y0 + y1) // 2,
                text=display_val, font=("Helvetica", 14, "bold")
            )

            self.cards_canvas.tag_bind(rect, "<Button-1>",
                                       lambda e, v=val: self.on_card_click(v))
            self.cards_canvas.tag_bind(text, "<Button-1>",
                                       lambda e, v=val: self.on_card_click(v))

            self.card_items.append((rect, text, val))

    def on_card_click(self, val):
        """Gère le clic sur une carte - IDENTIQUE À L'ORIGINAL"""
        parsed = utils.parse_card_input(str(val))
        if parsed is None:
            io_helpers.modal_error(self.root, "Erreur", f"Carte invalide: {val}")
            return

        # Register vote for current player (identique)
        self.votes_current_attempt.append(parsed)

        # advance player index (identique)
        self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            # all players voted -> evaluate this attempt
            self.evaluate_attempt()
        else:
            # continue to next player
            self.update_turn_label()

    # ---------- Évaluation des tentatives ----------
    def evaluate_attempt(self):
        """Évalue une tentative de vote - LOGIQUE IDENTIQUE À L'ORIGINAL"""
        if self.current_task_index >= len(self.state):
            return

        task = self.state[self.current_task_index]
        votes = self.votes_current_attempt.copy()

        # save this attempt in history_tmp (identique)
        self.history_tmp.append({
            "phase": "unanimity",
            "attempt": self.attempt,
            "votes": votes.copy(),
            "ts": int(time.time())
        })

        # coffee check (identique)
        if utils.all_coffee(votes):
            io_helpers.modal_info(self.root, "Pause",
                                  "Tous les joueurs ont choisi 'coffee'. Sauvegarde et pause.")

            save_path = io_helpers.modal_asksaveasfilename(self.root,
                                                           defaultextension=".json",
                                                           title="Nom du fichier de sauvegarde",
                                                           filetypes=[("JSON files", "*.json")])

            if save_path:
                save_obj = {
                    "timestamp": int(time.time()),
                    "players": self.players,
                    "mode": {"primary": self.mode_primary, "secondary": self.mode_secondary},
                    "state": [task.to_dict() for task in self.state],
                    "current_task_index": self.current_task_index,
                    "pause_info": {"timestamp": int(time.time()), "pause_seconds": config.PAUSE_SECONDS}
                }
                io_helpers.save_backlog_state(save_path, save_obj)
                io_helpers.modal_info(self.root, "Sauvegarde",
                                      f"État sauvegardé dans {save_path}. Pause enregistrée.")
            else:
                io_helpers.modal_warning(self.root, "Sauvegarde", "Sauvegarde annulée.")

            task.history.extend(self.history_tmp)
            self.reset_ui_after_pause()
            return

        # unanimity check (identique)
        if utils.all_same(votes):
            unanimous = votes[0]
            if unanimous == "?":
                io_helpers.modal_info(self.root, "Info",
                                      "Tous ont choisi '?'. Considéré comme non validé — nouvelle tentative.")
            elif unanimous == "coffee":
                pass  # Déjà géré ci-dessus
            else:
                task.estimation = unanimous
                task.history.extend(self.history_tmp)
                io_helpers.modal_info(self.root, "Résultat",
                                      f"Unanimité atteinte : estimation = {unanimous}")
                self.current_task_index += 1
                self.prepare_next_task_after_resolution()
                return
        else:
            io_helpers.modal_info(self.root, "Info", "Pas d'unanimité sur ce tour.")

        # If we reach here, unanimity not achieved or unanimous '?'.
        if self.attempt < config.MAX_UNANIM_ATTEMPTS:
            self.attempt += 1
            self.current_player_index = 0
            self.votes_current_attempt = []
            self.update_turn_label()
            return

        # attempt == MAX && no unanimous resolved -> apply secondary mode
        io_helpers.modal_info(self.root, "Info",
                              f"Aucune unanimité après {config.MAX_UNANIM_ATTEMPTS} tentatives. "
                              f"Passage au mode secondaire : {self.mode_secondary or 'fallback'}")

        last_votes = self.history_tmp[-1]["votes"] if self.history_tmp else votes

        # fallback (identique)
        if self.mode_secondary is None:
            self.handle_fallback_mode(task, last_votes)
            return

        # mean / median (identique)
        if self.mode_secondary in ("mean", "median"):
            self.handle_mean_median_mode(task, last_votes)
            return

        # absolute / relative (identique)
        if self.mode_secondary in ("absolute", "relative"):
            self.handle_majority_mode(task, last_votes)
            return

        # fallback as safety (identique)
        self.handle_fallback_mode(task, last_votes)

    def handle_fallback_mode(self, task, last_votes):
        """Gère le mode fallback - LOGIQUE IDENTIQUE À L'ORIGINAL"""
        nums = [v for v in last_votes if isinstance(v, int)]

        if nums:
            maj = utils.majority_by_frequency(last_votes)
            task.estimation = maj
            task.history.extend(self.history_tmp)
            io_helpers.modal_info(self.root, "Fallback",
                                  f"Attribution par fréquence : {maj}")
            self.current_task_index += 1
            self.prepare_next_task_after_resolution()
            return

        # Aucun vote numérique
        while True:
            io_helpers.modal_info(self.root, "Fallback",
                                  "Aucun vote numérique dans les derniers tours. "
                                  "Nouveau tour (entrez des valeurs numériques si possible).")

            votes = self.collect_votes_round_gui()
            self.history_tmp.append({
                "phase": "fallback",
                "votes": votes.copy(),
                "ts": int(time.time())
            })

            if utils.all_coffee(votes):
                self.handle_coffee_during_fallback(task)
                return

            nums = [v for v in votes if isinstance(v, int)]
            if nums:
                maj = utils.majority_by_frequency(votes)
                task.estimation = maj
                task.history.extend(self.history_tmp)
                io_helpers.modal_info(self.root, "Fallback",
                                      f"Attribution par fréquence : {maj}")
                self.current_task_index += 1
                self.prepare_next_task_after_resolution()
                return

    def handle_coffee_during_fallback(self, task):
        """Gère le café pendant le mode fallback - IDENTIQUE À L'ORIGINAL"""
        save_path = io_helpers.modal_asksaveasfilename(self.root,
                                                       defaultextension=".json", title="Nom du fichier de sauvegarde",
                                                       filetypes=[("JSON files", "*.json")])

        if save_path:
            save_obj = {
                "timestamp": int(time.time()),
                "players": self.players,
                "mode": {"primary": self.mode_primary, "secondary": self.mode_secondary},
                "state": [t.to_dict() for t in self.state],
                "current_task_index": self.current_task_index,
                "pause_info": {"timestamp": int(time.time()), "pause_seconds": config.PAUSE_SECONDS}
            }
            io_helpers.save_backlog_state(save_path, save_obj)
            io_helpers.modal_info(self.root, "Sauvegarde",
                                  f"État sauvegardé dans {save_path}. Pause enregistrée.")

        task.history.extend(self.history_tmp)
        self.reset_ui_after_pause()

    def handle_mean_median_mode(self, task, last_votes):
        """Gère les modes mean et median - LOGIQUE IDENTIQUE À L'ORIGINAL"""
        from statistics import mean, median

        nums = [v for v in last_votes if isinstance(v, int)]

        if not nums:
            # Demander de nouveaux votes numériques
            while True:
                io_helpers.modal_info(self.root, "Info",
                                      f"Pas de votes numériques pour calculer {self.mode_secondary}. "
                                      "Nouveau tour (valeurs numériques svp).")

                votes = self.collect_votes_round_gui()
                self.history_tmp.append({
                    "phase": self.mode_secondary,
                    "votes": votes.copy(),
                    "ts": int(time.time())
                })

                if utils.all_coffee(votes):
                    self.handle_coffee_during_fallback(task)
                    return

                nums = [v for v in votes if isinstance(v, int)]
                if nums:
                    break

                io_helpers.modal_info(self.root, "Info",
                                      "Toujours pas de votes numériques, on recommence.")

        # Calcul selon le mode
        if self.mode_secondary == "mean":
            m = mean(nums)
            chosen = utils.nearest_card_value(m)
            task.estimation = chosen
            task.history.extend(self.history_tmp)
            io_helpers.modal_info(self.root, "Mean",
                                  f"Moyenne = {m:.2f} -> carte la plus proche : {chosen}")
        else:  # median
            med = median(nums)
            chosen = utils.nearest_card_value(med)
            task.estimation = chosen
            task.history.extend(self.history_tmp)
            io_helpers.modal_info(self.root, "Median",
                                  f"Médiane = {med} -> carte la plus proche : {chosen}")

        self.current_task_index += 1
        self.prepare_next_task_after_resolution()

    def handle_majority_mode(self, task, last_votes):
        """Gère les modes absolute et relative - LOGIQUE IDENTIQUE À L'ORIGINAL"""
        from collections import Counter

        while True:
            io_helpers.modal_info(self.root, "Mode secondaire",
                                  f"Vote selon mode {self.mode_secondary}. Nouveau tour.")

            votes = self.collect_votes_round_gui()
            self.history_tmp.append({
                "phase": self.mode_secondary,
                "votes": votes.copy(),
                "ts": int(time.time())
            })

            if utils.all_coffee(votes):
                self.handle_coffee_during_fallback(task)
                return

            nums = [v for v in votes if isinstance(v, int)]
            if not nums:
                io_helpers.modal_info(self.root, "Info",
                                      "Aucun vote numérique dans ce tour. Recommencez.")
                continue

            cnt = Counter(nums)
            most_common_val, count = cnt.most_common(1)[0]

            if self.mode_secondary == "absolute":
                if count > len(self.players) / 2:
                    task.estimation = most_common_val
                    task.history.extend(self.history_tmp)
                    pct = count / len(self.players) * 100.0
                    io_helpers.modal_info(self.root, "Absolute",
                                          f"Majorité absolue atteinte pour {most_common_val} ({pct:.1f}%).")
                    self.current_task_index += 1
                    self.prepare_next_task_after_resolution()
                    return
                else:
                    io_helpers.modal_info(self.root, "Absolute",
                                          f"Pas de majorité absolue ({count}/{len(self.players)}). Re-votez.")
                    continue
            else:  # relative
                most = cnt.most_common()
                if len(most) == 1 or most[0][1] > most[1][1]:
                    task.estimation = most_common_val
                    task.history.extend(self.history_tmp)
                    io_helpers.modal_info(self.root, "Relative",
                                          f"Majorité relative atteinte pour {most_common_val} ({most[0][1]} votes).")
                    self.current_task_index += 1
                    self.prepare_next_task_after_resolution()
                    return
                else:
                    io_helpers.modal_info(self.root, "Relative",
                                          "Pas de majorité relative claire (ex-aequo). Re-votez.")
                    continue

    def collect_votes_round_gui(self):
        """Collecte un tour complet de votes - IDENTIQUE À L'ORIGINAL"""
        votes = []
        io_helpers.modal_info(self.root, "Nouveau tour",
                              "Tour de votes (mode secondaire). "
                              "Cliquez vos cartes dans l'ordre des joueurs.")

        for p_idx, p in enumerate(self.players):
            io_helpers.modal_info(self.root, "Tour joueur",
                                  f"C'est au tour de : {p}\n"
                                  "Cliquez la carte choisie dans la fenêtre principale.")

            clicked = []

            def tmp_handler(event, val=None):
                clicked.append(utils.parse_card_input(str(val)))

            # attach temporary handlers (identique)
            for rect, text, v in self.card_items:
                self.cards_canvas.tag_bind(rect, "<Button-1>",
                                           lambda e, vv=v: tmp_handler(e, vv))
                self.cards_canvas.tag_bind(text, "<Button-1>",
                                           lambda e, vv=v: tmp_handler(e, vv))

            # loop until clicked has one value (identique)
            while not clicked:
                self.root.update()
                time.sleep(0.05)

            # redraw to restore original handlers (identique)
            self.draw_cards()
            val = clicked[0]
            votes.append(val)

        return votes

    # ---------- Gestion de l'interface ----------
    def prepare_next_task_after_resolution(self):
        """Prépare la tâche suivante - IDENTIQUE À L'ORIGINAL"""
        self.votes_current_attempt = []
        self.history_tmp = []
        self.attempt = 1
        self.current_player_index = 0
        self.load_task()

    def reset_ui_after_pause(self):
        """Réinitialise l'interface après une pause - IDENTIQUE À L'ORIGINAL"""
        self.task_label.config(
            text="Partie mise en pause (sauvegardée). "
                 "Charger la sauvegarde pour reprendre.")
        self.info_label.config(text="")
        self.cards_canvas.delete("all")
        self.current_task_index = len(self.state)

    def next_task_manual(self):
        """Passe manuellement à la tâche suivante - IDENTIQUE À L'ORIGINAL"""
        if self.current_task_index >= len(self.state):
            io_helpers.modal_info(self.root, "Info", "Aucune tâche en cours.")
            return

        task = self.state[self.current_task_index]
        if task.estimation is not None:
            self.current_task_index += 1
            self.prepare_next_task_after_resolution()
            return

        res = io_helpers.modal_askyesno(self.root, "Passer tâche ?",
                                        "Cette tâche n'a pas d'estimation. "
                                        "Voulez-vous l'ignorer / passer et la laisser non estimée ? "
                                        "(Non pour annuler)")

        if res:
            task.history.extend(self.history_tmp)
            self.current_task_index += 1
            self.prepare_next_task_after_resolution()

    # ---------- Sauvegarde ----------
    def save_final_results(self):
        """Sauvegarde les résultats finaux - IDENTIQUE À L'ORIGINAL"""
        outpath = io_helpers.modal_asksaveasfilename(self.root,
                                                     defaultextension=".json",
                                                     title="Partie terminée - nom du fichier de sortie",
                                                     filetypes=[("JSON files", "*.json")])

        if outpath:
            final_obj = {
                "timestamp": int(time.time()),
                "players": self.players,
                "mode": {"primary": self.mode_primary, "secondary": self.mode_secondary},
                "state": [task.to_dict() for task in self.state],
                "current_task_index": self.current_task_index
            }

            io_helpers.save_backlog_state(outpath, final_obj)
            io_helpers.modal_info(self.root, "Sauvegarde",
                                  f"Résultats sauvegardés dans {outpath}. Merci et bon sprint !")
        else:
            io_helpers.modal_warning(self.root, "Annulé", "Sauvegarde finale annulée.")

        self.task_label.config(text="Partie terminée.")
        self.info_label.config(text="")
        self.cards_canvas.delete("all")