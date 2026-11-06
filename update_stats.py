import json
import urllib.request

def fetch_euroleague_data():
    print("Inizio recupero dati Euroleague...")
    
    players_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/players/traditional?seasonMode=Single&limit=1000&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    
    players_data = []
    teams_data = []

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

                # Estrazione tiri da 2 e da 3
                t2m = p.get("twoPointersMade", 0)
                t2a = p.get("twoPointersAttempted", 0)
                t3m = p.get("threePointersMade", 0)
                t3a = p.get("threePointersAttempted", 0)
                
                # Calcolo tiri totali (Field Goals)
                fgm = round(t2m + t3m, 1)
                fga = round(t2a + t3a, 1)

                player_entry = {
                    "Player": name,
                    "Team": team_code,
                    "GP": p.get("gamesPlayed", 0),
                    "MIN": p.get("minutesPlayed", 0),
                    "PTS": p.get("pointsScored", 0),
                    "OREB": p.get("offensiveRebounds", 0),
                    "DREB": p.get("defensiveRebounds", 0),
                    "REB": p.get("totalRebounds", 0),
                    "AST": p.get("assists", 0),
                    "STL": p.get("steals", 0),
                    "BLK": p.get("blocks", 0),
                    "PF": p.get("foulsCommited", 0),
                    "2PM": t2m,
                    "2PA": t2a,
                    "3PM": t3m,
                    "3PA": t3a,
                    "FGM": fgm,
                    "FGA": fga,
                    "FTM": p.get("freeThrowsMade", 0),
                    "FTA": p.get("freeThrowsAttempted", 0),
                    "TO": p.get("turnovers", 0),
                    "PIR": p.get("pir", 0)
                }
                players_data.append(player_entry)
                
    except Exception as e:
        print(f"Errore durante il recupero dei dati: {e}")

    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("euroleague-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print(f"File aggiornato con successo! {len(players_data)} giocatori elaborati.")

if __name__ == "__main__":
    fetch_euroleague_data()
