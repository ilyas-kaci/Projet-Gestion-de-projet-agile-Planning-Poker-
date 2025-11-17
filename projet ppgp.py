
# planning_poker.py
"""
Application de Planning Poker (local, tour-par-tour).
Usage: python planning_poker.py
"""

import json
import time
import math
from statistics import median, mean
from collections import Counter, defaultdict

CARDS = [0,1,2,3,5,8,13,20,40,100]
SPECIAL_CARDS = ["?", "coffee"]
ALL_CARDS = [str(c) for c in CARDS] + SPECIAL_CARDS

# --- Helpers de mapping/arrondi ---
def parse_card_input(s):
    """
    Convertit la saisie utilisateur en valeur utilisable:
    - numériques -> int
    - "?" -> "?"
    - "coffee" -> "coffee"
    Retourne str pour spéciaux, int pour numériques.
    """
    s = s.strip()
    if s.lower() == "?" or s == "?":
        return "?"
    if s.lower() in ("coffee", "café", "cafe"):
        return "coffee"
    try:
        v = int(s)
        if v in CARDS:
            return v
        else:
            return None
    except ValueError:
        return None

def nearest_card_value(val):
    """Donne la valeur de carte la plus proche (pour moyenne/médiane si nécessaire)."""
    if val is None:
        return None
    # si val déjà dans CARDS, renvoie directement
    try:
        v = float(val)
    except Exception:
        return None
    diffs = [(abs(v - c), c) for c in CARDS]
    diffs.sort(key=lambda x: (x[0], x[1]))
    return diffs[0][1]

def majority_by_frequency(votes):
    """
    votes: list de valeurs (mix int et spéciaux)
    Retourne la valeur majoritaire numérique si possible (ignore "?" et "coffee" pour décider).
    Si pas de vote numérique, renvoie None.
    En cas d'égalité, renvoie la valeur numérique la plus élevée parmi les ex-aequo (choix arbitraire raisonnable).
    """
    nums = [v for v in votes if isinstance(v, int)]
    if not nums:
        return None
    cnt = Counter(nums)
    most_common = cnt.most_common()
    highest_count = most_common[0][1]
    tied = [val for val,count in most_common if count == highest_count]
    return max(tied)  # tiebreaker : choisir la valeur la plus élevée

def percent_of_value(votes, value):
    """Pourcentage des votes égaux à value (sur total joueurs)."""
    return votes.count(value) / len(votes) * 100

# --- I/O backlog ---
def load_backlog_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # attendu: liste d'objets { "id": "...", "title": "...", "description": "..."}
    if isinstance(data, dict):
        # autoriser dict contenant "backlog": [...]
        if "backlog" in data and isinstance(data["backlog"], list):
            return data["backlog"]
        # try to find list inside dict
        for v in data.values():
            if isinstance(v, list):
                return v
    if isinstance(data, list):
        return data
    raise ValueError("Format JSON du backlog non supporté (attendu liste ou {'backlog': [...]})")

def save_backlog_state(path, backlog_state):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(backlog_state, f, ensure_ascii=False, indent=2)

# --- Menu & interactions ---
def input_int(prompt, minv=None, maxv=None):
    while True:
        try:
            v = int(input(prompt))
            if minv is not None and v < minv:
                print(f"Doit être >= {minv}")
                continue
            if maxv is not None and v > maxv:
                print(f"Doit être <= {maxv}")
                continue
            return v
        except ValueError:
            print("Entrez un nombre entier valide.")

def choose_mode():
    print("\nChoisissez le mode de jeu (obligatoire: strict + un autre) :")
    print("1) Strict (unanimité)")
    print("2) Moyenne")
    print("3) Médiane")
    print("4) Majorité absolue (>50%)")
    print("5) Majorité relative (plus de voix que les autres)")
    while True:
        v = input_int("Entrez le numéro du mode principal (1-5) : ", 1, 5)
        if v == 1:
            # strict + choisir aussi un second mode facultatif
            print("Vous avez choisi 'Strict'. Choisissez un second mode parmi (2-5) ou 1 pour seulement strict :")
            v2 = input_int("Second mode (1 pour seulement strict) : ", 1, 5)
            if v2 == 1:
                return ("strict", None)
            modes_map = {2: "mean", 3: "median", 4: "absolute", 5: "relative"}
            return ("strict", modes_map[v2])
        else:
            modes_map = {2: "mean", 3: "median", 4: "absolute", 5: "relative"}
            return ("strict", modes_map[v])  # on garde 'strict' comme mode 1er-tour + second mode

def print_cards():
    print("Cartes disponibles : " + ", ".join(str(c) for c in CARDS) + ", ?, coffee")

# --- Partie centrale : résolution d'une tâche ---
def play_task_round(task, players, mode_secondary):
    """
    task: dict
    players: list of player names
    mode_secondary: "mean"|"median"|"absolute"|"relative"|None
    Retourne estimation finale (int or None if saved via coffee) et historique tours.
    """
    history = []
    attempt = 1
    MAX_ATTEMPTS = 3

    while True:
        print("\n--- Estimation pour :", task.get("title", task.get("id", "<no-title>")), f"(tentative {attempt}) ---")
        votes = []
        for p in players:
            print(f"\nJoueur : {p} -> à toi (tour local, cache ton choix).")
            print_cards()
            while True:
                s = input(f"{p}, entre ta carte (ex: 3, 5, ?, coffee) : ").strip()
                parsed = parse_card_input(s)
                if parsed is None:
                    print("Entrée invalide. Réessaie.")
                    continue
                votes.append(parsed)
                break

        history.append({"attempt": attempt, "votes": votes.copy()})

        # si tous coffee -> sauvegarde et quitte pour reprise
        if all(v == "coffee" for v in votes):
            print("\n> Tous les joueurs ont choisi 'coffee'. On sauvegarde l'état et on met en pause.")
            return {"status": "paused", "history": history, "estimation": None}

        # check unanimity
        if all(v == votes[0] for v in votes):
            unanimous = votes[0]
            if unanimous == "?":
                # if unanimous '?', ask group to discuss and re-vote (but per rules it's unanimity -> treat as unresolved)
                print("Tous ont choisi '?'. Ceci est considéré comme non validé — on continue le vote.")
            elif unanimous == "coffee":
                # handled above
                pass
            else:
                # unanimous numeric value
                print(f"Unanimité atteinte : estimation = {unanimous}")
                return {"status": "resolved", "history": history, "estimation": unanimous}
        # not unanimous
        print("Pas d'unanimité sur ce tour.")
        # If we've reached attempt 1, rules say: first tour should be unanimity for non-strict modes as well.
        # For attempt >1, apply chosen secondary mode (if any).
        # === Gestion des tentatives ===
        if attempt < MAX_ATTEMPTS:
            # Tant qu'on n'a pas fait 3 tentatives, on exige l'unanimité
            print(f"Unanimité non atteinte (tentative {attempt}/{MAX_ATTEMPTS}). On discute et on recommence.")
            attempt += 1
            continue
        else:
            # Après 3 tentatives sans unanimité, on applique la règle secondaire
            print(f"Pas d'unanimité après {MAX_ATTEMPTS} tentatives.")
            nums = [v for v in votes if isinstance(v, int)]
            if not nums:
                print("Aucun vote numérique disponible pour appliquer une règle secondaire.")
                return {"status": "unresolved", "history": history, "estimation": None}

            # === Mode strict uniquement → majorité de fréquence ===
            if mode_secondary is None:
                maj = majority_by_frequency(votes)
                pct = percent_of_value(votes, maj) if maj is not None else 0
                print(f"Mode strict → application de la règle de majorité : {maj} ({pct:.1f}%)")
                return {"status": "resolved", "history": history, "estimation": maj}

            # === Application du mode secondaire ===
            if mode_secondary == "mean":
                m = mean(nums)
                chosen = nearest_card_value(m)
                print(f"Moyenne = {m:.2f} → carte la plus proche : {chosen}")
                return {"status": "resolved", "history": history, "estimation": chosen}

            if mode_secondary == "median":
                med = median(nums)
                chosen = nearest_card_value(med)
                print(f"Médiane = {med} → carte la plus proche : {chosen}")
                return {"status": "resolved", "history": history, "estimation": chosen}

            if mode_secondary == "absolute":
                cnt = Counter(nums)
                most_common_val, count = cnt.most_common(1)[0]
                if count > len(players) / 2:
                    pct = count / len(players) * 100
                    print(f"Majorité absolue atteinte pour {most_common_val} ({pct:.1f}%).")
                    return {"status": "resolved", "history": history, "estimation": most_common_val}
                else:
                    print("Pas de majorité absolue, on prend la valeur la plus fréquente par défaut.")
                    maj = majority_by_frequency(votes)
                    return {"status": "resolved", "history": history, "estimation": maj}

            if mode_secondary == "relative":
                cnt = Counter(nums)
                most_common_val, count = cnt.most_common(1)[0]
                print(f"Majorité relative : {most_common_val} ({count} votes)")
                return {"status": "resolved", "history": history, "estimation": most_common_val}

            # Fallback
            maj = majority_by_frequency(votes)
            print(f"Règle secondaire inconnue → majorité de fréquence : {maj}")
            return {"status": "resolved", "history": history, "estimation": maj}


# --- Flow principal ---
def main():
    print("=== Planning Poker (local) ===")
    players = []
    while True:
        n = input_int("Nombre de joueurs (>=2) : ", 2)
        for i in range(n):
            name = input(f"Pseudo joueur {i+1} : ").strip() or f"Player{i+1}"
            players.append(name)
        break

    mode_primary, mode_secondary = choose_mode()
    if mode_secondary is None:
        print(f"Mode choisi: Strict (unanimité).")
    else:
        print(f"Mode choisi: Strict (1er tour) + {mode_secondary} (tours suivants).")

    backlog = []
    # menu pour charger backlog ou en créer un échantillon
    while True:
        print("\nMenu :")
        print("1) Charger backlog depuis un fichier JSON")
        print("2) Créer un backlog simple manuellement")
        print("3) Quitter")
        choice = input_int("Choix : ", 1, 3)
        if choice == 1:
            path = input("Chemin du fichier JSON de backlog : ").strip()
            try:
                backlog = load_backlog_from_file(path)
                print(f"Backlog chargé : {len(backlog)} éléments.")
                break
            except Exception as e:
                print("Erreur en chargeant le backlog :", e)
                continue
        elif choice == 2:
            m = input_int("Combien de tâches ajouter ? ", 1)
            for i in range(m):
                t = input(f"Titre tâche {i+1} : ").strip() or f"Tâche {i+1}"
                desc = input("Description (optionnelle) : ").strip()
                backlog.append({"id": f"t{i+1}", "title": t, "description": desc})
            break
        else:
            print("Au revoir.")
            return

    # état d'avancement : on stocke chaque tâche avec statut
    state = []
    for t in backlog:
        state.append({
            "id": t.get("id"),
            "title": t.get("title"),
            "description": t.get("description"),
            "estimation": None,
            "history": []
        })

    # option : reprendre partie sauvegardée?
    # loop through backlog items not yet estimated
    for item in state:
        if item["estimation"] is not None:
            continue
        result = play_task_round(item, players, mode_secondary)
        if result["status"] == "paused":
            # sauvegarder fichier avec état courant
            savepath = input("Nom du fichier de sauvegarde (ex: save_backlog.json) : ").strip() or "save_backlog.json"
            # build save structure: remaining items with current histories
            # attach history for current item
            item["history"] = result["history"]
            # create save object
            save_obj = {
                "timestamp": int(time.time()),
                "players": players,
                "mode": {"primary": mode_primary, "secondary": mode_secondary},
                "state": state
            }
            save_backlog_state(savepath, save_obj)
            print(f"État sauvegardé dans {savepath}. Vous pouvez reprendre plus tard via le menu.")
            return
        elif result["status"] == "resolved":
            item["estimation"] = result["estimation"]
            item["history"] = result["history"]
            print(f"Estimation finale pour '{item['title']}' = {item['estimation']}")
        else:
            print(f"Aucune estimation trouvée pour '{item['title']}'. On la laisse non estimée.")
            item["history"] = result["history"]

    # tout le backlog estimé -> sauvegarder résultat final
    outpath = input("Partie terminée. Nom du fichier de sortie (ex: result_backlog.json) : ").strip() or "result_backlog.json"
    final_obj = {
        "timestamp": int(time.time()),
        "players": players,
        "mode": {"primary": mode_primary, "secondary": mode_secondary},
        "state": state
    }
    save_backlog_state(outpath, final_obj)
    print(f"Résultats sauvegardés dans {outpath}. Merci et bon sprint !")

if __name__ == "__main__":
    main()
