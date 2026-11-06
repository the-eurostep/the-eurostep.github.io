import json
import urllib.request
from collections import defaultdict

TEAM_NAMES = {
    "ZAL": "ZALGIRIS",
    "VIR": "VIRTUS BOLOGNA",
    "ULK": "FENERBAHCE",
    "TEL": "MACCABI TEL AVIV",
    "RED": "RED STAR",
    "PRS": "PARIS",
    "PAR": "PARTIZAN",
    "PAN": "PANATHINAIKOS",
    "PAM": "VALENCIA",
    "OLY": "OLYMPIACOS",
    "MUN": "BAYERN MUNICH",
    "MIL": "OLIMPIA MILAN",
    "MAD": "REAL MADRID",
    "IST": "ANADOLU EFES",
    "HTA": "HAPOEL TEL AVIV",
    "DUB": "DUBAI",
    "BES": "BESIKTAS",
    "BAS": "BASKONIA",
    "BAR": "BARCELONA",
    "ASV": "ASVEL"
}

def fetch_euroleague_data():
    print("Inizio recupero dati Euroleague...")
    
    players_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/players/traditional?seasonMode=Single&limit=1000&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    
    players_data = []
    
    # Struttura per accumulare i totali ponderati per squadra
    team_aggregates = defaultdict(lambda: {
        "total_gp": 0, "player_count": 0,
        "MIN": 0, "PTS": 0, "OREB": 0, "DREB": 0, "REB": 0,
        "AST": 0, "STL": 0, "BLK": 0, "PF": 0, "2PM": 0, "2PA": 0,
        "3PM": 0, "3PA": 0, "FTM": 0, "FTA": 0, "TO": 0
    })

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }

    try:
        req_players = urllib.request.Request(players_url, headers=headers)
        with urllib.request.urlopen(req_players) as response:
            raw_data = json.loads(response.read().decode('utf-8'))
            
            if isinstance(raw_data, list):
                items = raw_data
            elif isinstance(raw_data, dict):
                items = raw_data.get('data', raw_data.get('players', []))
                if isinstance(items, dict):
                    items = items.get('data', items.get('items', []))
            else:
                items = []

            for p in items:
                person = p.get("player", {})
                
                name = person.get("name") or f"{person.get('firstName', '')} {person.get('lastName', '')}".strip()
                if not name or name == " ":
                    name = "Unknown"

                team_code = person.get("team", {}).get("code", "")
                team_full_name = TEAM_NAMES.get(team_code, team_code if team_code else "UNKNOWN TEAM")

                gp = p.get("gamesPlayed", 0) or 0
                min_val = p.get("minutesPlayed", 0) or 0
                pts = p.get("pointsScored", 0) or 0
                oreb = p.get("offensiveRebounds", 0) or 0
                dreb = p.get("defensiveRebounds", 0) or 0
                reb = p.get("totalRebounds", 0) or 0
                ast = p.get("assists", 0) or 0
                stl = p.get("steals", 0) or 0
                blk = p.get("blocks", 0) or 0
                pf = p.get("foulsCommited", 0) or 0
                t2m = p.get("twoPointersMade", 0) or 0
                t2a = p.get("twoPointersAttempted", 0) or 0
                t3m = p.get("threePointersMade", 0) or 0
                t3a = p.get("threePointersAttempted", 0) or 0
                ftm = p.get("freeThrowsMade", 0) or 0
                fta = p.get("freeThrowsAttempted", 0) or 0
                to_val = p.get("turnovers", 0) or 0
                pir = p.get("pir", 0) or 0

                # Dati singoli giocatore (invariati)
                player_entry = {
                    "Player": name,
                    "Team": team_code,
                    "GP": gp,
                    "MIN": min_val,
                    "PTS": pts,
                    "OREB": oreb,
                    "DREB": dreb,
                    "REB": reb,
                    "AST": ast,
                    "STL": stl,
                    "BLK": blk,
                    "PF": pf,
                    "2PM": t2m,
                    "2PA": t2a,
                    "3PM": t3m,
                    "3PA": t3a,
                    "FGM": round(t2m + t3m, 1),
                    "FGA": round(t2a + t3a, 1),
                    "FTM": ftm,
                    "FTA": fta,
                    "TO": to_val,
                    "PIR": pir
                }
                players_data.append(player_entry)

                # Aggregazione ponderata per squadra (moltiplicando per le partite giocate del giocatore)
                if team_full_name and team_full_name != "UNKNOWN TEAM" and gp > 0:
                    t = team_aggregates[team_full_name]
                    t["max_gp"] = max(t.get("max_gp", 0), gp)
                    t["total_gp_sum"] += gp
                    t["player_count"] += 1
                    
                    # Accumuliamo il volume totale moltiplicando la media del giocatore per le sue partite
                    t["MIN"] += min_val * gp
                    t["PTS"] += pts * gp
                    t["OREB"] += oreb * gp
                    t["DREB"] += dreb * gp
                    t["REB"] += reb * gp
                    t["AST"] += ast * gp
                    t["STL"] += stl * gp
                    t["BLK"] += blk * gp
                    t["PF"] += pf * gp
                    t["2PM"] += t2m * gp
                    t["2PA"] += t2a * gp
                    t["3PM"] += t3m * gp
                    t["3PA"] += t3a * gp
                    t["FTM"] += ftm * gp
                    t["FTA"] += fta * gp
                    t["TO"] += to_val * gp

    except Exception as e:
        print(f"Errore durante il recupero dei dati: {e}")

    # Calcolo finale delle medie squadra dividendo per il totale delle partite o normalizzando
    teams_data = []
    for team_name, stats in team_aggregates.items():
        # Usiamo il massimo delle partite giocate dai giocatori chiave come base partita della squadra
        gp_base = stats.get("max_gp", 1)
        if gp_base == 0:
            gp_base = 1

        # Il volume totale diviso per le partite della squadra ci dà la media per partita corretta e ponderata
        teams_data.append({
            "Team": team_name,
            "GP": gp_base,
            "PTS": round(stats["PTS"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0, # Media ponderata robusta per partita
            "OREB": round(stats["OREB"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "DREB": round(stats["DREB"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "REB": round(stats["REB"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "AST": round(stats["AST"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "STL": round(stats["STL"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "BLK": round(stats["BLK"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "PF": round(stats["PF"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "2PM": round(stats["2PM"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "2PA": round(stats["2PA"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "3PM": round(stats["3PM"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "3PA": round(stats["3PA"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "FGM": round((stats["2PM"] + stats["3PM"]) / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "FGA": round((stats["2PA"] + stats["3PA"]) / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "FTM": round(stats["FTM"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "FTA": round(stats["FTA"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0,
            "TO": round(stats["TO"] / stats["total_gp_sum"] * (stats["total_gp_sum"] / stats["player_count"]), 1) if stats["player_count"] > 0 else 0
        })

    # Ordinamento per punti decrescente
    teams_data.sort(key=lambda x: x["PTS"], reverse=True)

    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("euroleague-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print(f"File aggiornato con successo! {len(players_data)} giocatori e {len(teams_data)} squadre elaborate.")

if __name__ == "__main__":
    fetch_euroleague_data()
