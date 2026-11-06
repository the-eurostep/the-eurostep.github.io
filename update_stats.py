import json
import urllib.request

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
    print("Inizio recupero dati ufficiali Euroleague...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }

    players_data = []
    teams_data = []

    # 1. RECUPERO DATI GIOCATORI
    players_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/players/traditional?seasonMode=Single&limit=1000&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    try:
        req_p = urllib.request.Request(players_url, headers=headers)
        with urllib.request.urlopen(req_p) as response:
            raw_p = json.loads(response.read().decode('utf-8'))
            items_p = raw_p if isinstance(raw_p, list) else raw_p.get('data', raw_p.get('players', []))
            if isinstance(items_p, dict):
                items_p = items_p.get('data', items_p.get('items', []))

            for p in items_p:
                person = p.get("player", {})
                name = person.get("name") or f"{person.get('firstName', '')} {person.get('lastName', '')}".strip()
                if not name or name == " ": name = "Unknown"

                team_code = person.get("team", {}).get("code", "")
                
                t2m = p.get("twoPointersMade", 0) or 0
                t2a = p.get("twoPointersAttempted", 0) or 0
                t3m = p.get("threePointersMade", 0) or 0
                t3a = p.get("threePointersAttempted", 0) or 0

                players_data.append({
                    "Player": name,
                    "Team": team_code, # Sigla breve per i giocatori
                    "GP": p.get("gamesPlayed", 0) or 0,
                    "MIN": p.get("minutesPlayed", 0) or 0,
                    "PTS": p.get("pointsScored", 0) or 0,
                    "OREB": p.get("offensiveRebounds", 0) or 0,
                    "DREB": p.get("defensiveRebounds", 0) or 0,
                    "REB": p.get("totalRebounds", 0) or 0,
                    "AST": p.get("assists", 0) or 0,
                    "STL": p.get("steals", 0) or 0,
                    "BLK": p.get("blocks", 0) or 0,
                    "PF": p.get("foulsCommited", 0) or 0,
                    "2PM": t2m,
                    "2PA": t2a,
                    "3PM": t3m,
                    "3PA": t3a,
                    "FGM": round(t2m + t3m, 1),
                    "FGA": round(t2a + t3a, 1),
                    "FTM": p.get("freeThrowsMade", 0) or 0,
                    "FTA": p.get("freeThrowsAttempted", 0) or 0,
                    "TO": p.get("turnovers", 0) or 0,
                    "PIR": p.get("pir", 0) or 0
                })
        print(f"Scaricati {len(players_data)} giocatori con successo.")
    except Exception as e:
        print(f"Errore recupero giocatori: {e}")

    # 2. RECUPERO DATI SQUADRE (UFFICIALI)
    teams_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/teams/traditional?seasonMode=Single&limit=100&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    try:
        req_t = urllib.request.Request(teams_url, headers=headers)
        with urllib.request.urlopen(req_t) as response:
            raw_t = json.loads(response.read().decode('utf-8'))
            items_t = raw_t.get('teams', [])

            for t in items_t:
                t_info = t.get("team", {})
                code = t_info.get("code", "")
                # Assegniamo il nome in CAPS LOCK basato sul dizionario o sul nome nativo
                full_name = TEAM_NAMES.get(code, t_info.get("name", "UNKNOWN TEAM").upper())

                t2m = t.get("twoPointersMade", 0) or 0
                t2a = t.get("twoPointersAttempted", 0) or 0
                t3m = t.get("threePointersMade", 0) or 0
                t3a = t.get("threePointersAttempted", 0) or 0

                teams_data.append({
                    "Team": full_name, # Nome completo in CAPS LOCK per le squadre
                    "GP": t.get("gamesPlayed", 0) or 0,
                    "PTS": t.get("pointsScored", 0) or 0,
                    "OREB": t.get("offensiveRebounds", 0) or 0,
                    "DREB": t.get("defensiveRebounds", 0) or 0,
                    "REB": t.get("totalRebounds", 0) or 0,
                    "AST": t.get("assists", 0) or 0,
                    "STL": t.get("steals", 0) or 0,
                    "BLK": t.get("blocks", 0) or 0,
                    "PF": t.get("foulsCommited", 0) or 0,
                    "2PM": t2m,
                    "2PA": t2a,
                    "3PM": t3m,
                    "3PA": t3a,
                    "FGM": round(t2m + t3m, 1),
                    "FGA": round(t2a + t3a, 1),
                    "FTM": t.get("freeThrowsMade", 0) or 0,
                    "FTA": t.get("freeThrowsAttempted", 0) or 0,
                    "TO": t.get("turnovers", 0) or 0
                })
        print(f"Scaricate {len(teams_data)} squadre con successo.")
    except Exception as e:
        print(f"Errore recupero squadre: {e}")

    # Salvataggio finale del file JSON unificato
    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("euroleague-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print("File euroleague-data.json generato perfettamente!")

if __name__ == "__main__":
    fetch_euroleague_data()
