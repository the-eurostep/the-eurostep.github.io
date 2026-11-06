import json
import urllib.request
from collections import defaultdict

TEAM_NAMES = {
    "ZAL": "Zalgiris",
    "VIR": "Virtus Bologna",
    "ULK": "Fenerbahce",
    "TEL": "Maccabi Tel Aviv",
    "RED": "Red Star",
    "PRS": "Paris",
    "PAR": "Partizan",
    "PAN": "Panathinaikos",
    "PAM": "Valencia",
    "OLY": "Olympiacos",
    "MUN": "Bayern Munich",
    "MIL": "Olimpia Milan",
    "MAD": "Real Madrid",
    "IST": "Anadolu Efes",
    "HTA": "Hapoel Tel Aviv",
    "DUB": "Dubai",
    "BES": "Besiktas",
    "BAS": "Baskonia",
    "BAR": "Barcelona",
    "ASV": "ASVEL"
}

def fetch_euroleague_data():
    print("Inizio recupero dati Euroleague...")
    
    players_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/players/traditional?seasonMode=Single&limit=1000&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    
    players_data = []
    team_aggregates = defaultdict(lambda: {
        "GP_count": 0, "MIN": 0, "PTS": 0, "OREB": 0, "DREB": 0, "REB": 0,
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
                team_full_name = TEAM_NAMES.get(team_code, team_code if team_code else "Unknown Team")

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
                fgm = round(t2m + t3m, 1)
                fga = round(t2a + t3a, 1)
                ftm = p.get("freeThrowsMade", 0) or 0
                fta = p.get("freeThrowsAttempted", 0) or 0
                to_val = p.get("turnovers", 0) or 0
                pir = p.get("pir", 0) or 0

                # Dati Giocatore
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
                    "FGM": fgm,
                    "FGA": fga,
                    "FTM": ftm,
                    "FTA": fta,
                    "TO": to_val,
                    "PIR": pir
                }
                players_data.append(player_entry)

                # Aggregazione per Squadra
                if team_full_name and team_full_name != "Unknown Team":
                    t = team_aggregates[team_full_name]
                    t["GP_max"] = max(t.get("GP_max", 0), gp) # Prendiamo il massimo delle partite giocate dai giocatori chiave come riferimento GP
                    t["MIN"] += min_val
                    t["PTS"] += pts
                    t["OREB"] += oreb
                    t["DREB"] += dreb
                    t["REB"] += reb
                    t["AST"] += ast
                    t["STL"] += stl
                    t["BLK"] += blk
                    t["PF"] += pf
                    t["2PM"] += t2m
                    t["2PA"] += t2a
                    t["3PM"] += t3m
                    t["3PA"] += t3a
                    t["FTM"] += ftm
                    t["FTA"] += fta
                    t["TO"] += to_val

    except Exception as e:
        print(f"Errore durante il recupero dei dati: {e}")

    # Formattazione finale dati squadre
    teams_data = []
    for team_name, stats in team_aggregates.items():
        teams_data.append({
            "Team": team_name,
            "GP": stats.get("GP_max", 0),
            "PTS": round(stats["PTS"], 1),
            "OREB": round(stats["OREB"], 1),
            "DREB": round(stats["DREB"], 1),
            "REB": round(stats["REB"], 1),
            "AST": round(stats["AST"], 1),
            "STL": round(stats["STL"], 1),
            "BLK": round(stats["BLK"], 1),
            "PF": round(stats["PF"], 1),
            "2PM": round(stats["2PM"], 1),
            "2PA": round(stats["2PA"], 1),
            "3PM": round(stats["3PM"], 1),
            "3PA": round(stats["3PA"], 1),
            "FGM": round(stats["2PM"] + stats["3PM"], 1),
            "FGA": round(stats["2PA"] + stats["3PA"], 1),
            "FTM": round(stats["FTM"], 1),
            "FTA": round(stats["FTA"], 1),
            "TO": round(stats["TO"], 1)
        })

    # Ordiniamo le squadre per punti in modo decrescente
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
