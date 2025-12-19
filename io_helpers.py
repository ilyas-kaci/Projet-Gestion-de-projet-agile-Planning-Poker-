#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file io_helpers.py
@brief Gestion des fichiers et dialogues modaux pour Planning Poker.
@details Ce module contient les fonctions pour charger/sauvegarder des fichiers JSON
et gérer les dialogues utilisateur avec tkinter.

@author DJERDI Ilyas Kaci, SEDDIK Oussama
@version 1.0.0
@date Décembre 2025

@note Utilise tkinter pour les dialogues modaux (nécessite interface graphique).
"""

import json
import tkinter as tk
from tkinter import filedialog


# --- I/O backlog helpers ---
def load_backlog_from_file(path):
    """Charge un backlog depuis un fichier JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        if "backlog" in data and isinstance(data["backlog"], list):
            return data["backlog"]
        for v in data.values():
            if isinstance(v, list):
                return v
    if isinstance(data, list):
        return data
    raise ValueError("Format JSON du backlog non supporté (attendu liste ou {'backlog': [...]})")


def save_backlog_state(path, backlog_state):
    """Sauvegarde l'état du backlog dans un fichier"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(backlog_state, f, ensure_ascii=False, indent=2)


def load_saved_state(path):
    """Charge un état sauvegardé"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict) or "state" not in data or "players" not in data or "mode" not in data:
        raise ValueError("Fichier de sauvegarde invalide.")
    return data


# --- Modal dialog helpers ---
def modal_center(parent, win):
    """Centre une fenêtre modale sur son parent"""
    win.update_idletasks()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    ww = win.winfo_width()
    wh = win.winfo_height()
    x = px + max(0, (pw - ww) // 2)
    y = py + max(0, (ph - wh) // 2)
    win.geometry(f"+{x}+{y}")


def modal_askstring(parent, title, prompt, initialvalue=""):
    """Dialogue modal pour demander une chaîne de caractères"""
    win = tk.Toplevel(parent)
    win.transient(parent)
    win.title(title or "")
    win.resizable(False, False)

    lbl = tk.Label(win, text=prompt)
    lbl.pack(padx=12, pady=(12, 6))

    entry = tk.Entry(win)
    entry.insert(0, initialvalue)
    entry.pack(padx=12, pady=(0, 12))

    result = {"val": None}

    def on_ok():
        result["val"] = entry.get()
        win.destroy()

    def on_cancel():
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=(0, 12))
    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Annuler", width=10, command=on_cancel).pack(side="left", padx=6)

    win.protocol("WM_DELETE_WINDOW", on_cancel)
    win.grab_set()
    win.lift()
    win.focus_force()
    modal_center(parent, win)
    entry.focus_set()
    parent.wait_window(win)

    return result["val"]


def modal_askinteger(parent, title, prompt, minvalue=None, maxvalue=None):
    """Dialogue modal pour demander un entier"""
    while True:
        s = modal_askstring(parent, title, prompt, initialvalue="")
        if s is None:
            return None
        try:
            v = int(s)
            if minvalue is not None and v < minvalue:
                modal_info(parent, "Erreur", f"Doit être >= {minvalue}")
                continue
            if maxvalue is not None and v > maxvalue:
                modal_info(parent, "Erreur", f"Doit être <= {maxvalue}")
                continue
            return v
        except ValueError:
            modal_info(parent, "Erreur", "Entrez un nombre entier valide.")
            continue


def modal_askyesno(parent, title, prompt):
    """Dialogue modal pour demander Oui/Non"""
    win = tk.Toplevel(parent)
    win.transient(parent)
    win.title(title or "")
    win.resizable(False, False)

    lbl = tk.Label(win, text=prompt, justify="left", wraplength=400)
    lbl.pack(padx=12, pady=(12, 10))

    result = {"val": False}

    def on_yes():
        result["val"] = True
        win.destroy()

    def on_no():
        result["val"] = False
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=(0, 12))
    tk.Button(btn_frame, text="Oui", width=10, command=on_yes).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Non", width=10, command=on_no).pack(side="left", padx=6)

    win.protocol("WM_DELETE_WINDOW", on_no)
    win.grab_set()
    win.lift()
    win.focus_force()
    modal_center(parent, win)
    parent.wait_window(win)

    return result["val"]


def modal_info(parent, title, message):
    """Dialogue modal d'information"""
    win = tk.Toplevel(parent)
    win.transient(parent)
    win.title(title or "")
    win.resizable(False, False)

    lbl = tk.Label(win, text=message, justify="left", wraplength=400)
    lbl.pack(padx=12, pady=(12, 10))

    def on_ok():
        win.destroy()

    tk.Button(win, text="OK", width=10, command=on_ok).pack(pady=(0, 12))

    win.protocol("WM_DELETE_WINDOW", on_ok)
    win.grab_set()
    win.lift()
    win.focus_force()
    modal_center(parent, win)
    parent.wait_window(win)


def modal_warning(parent, title, message):
    """Dialogue modal d'avertissement"""
    modal_info(parent, title, message)


def modal_error(parent, title, message):
    """Dialogue modal d'erreur"""
    modal_info(parent, title, message)


def modal_askopenfilename(parent, **kwargs):
    """Dialogue modal pour ouvrir un fichier"""
    parent.lift()
    parent.focus_force()
    filename = filedialog.askopenfilename(parent=parent, **kwargs)
    return filename


def modal_asksaveasfilename(parent, **kwargs):
    """Dialogue modal pour sauvegarder un fichier"""
    parent.lift()
    parent.focus_force()
    filename = filedialog.asksaveasfilename(parent=parent, **kwargs)
    return filename