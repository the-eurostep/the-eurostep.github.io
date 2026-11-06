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
            
            # Estrazione della lista dei giocatori
            if isinstance(raw_data, list):
                items = raw_data
            elif isinstance(raw_data, dict):
                items = raw_data.get('data', raw_data.get('players', []))
                if isinstance(items, dict):
                    items = items.get('data', items.get('items', []))
            else:
                items = []

            for p in items:
                # Estrazione dati anagrafici dal blocco "player"
                person = p.get("player", {})
                
                name = person.get("name") or f"{person.get('firstName', '')} {person.get('lastName', '')}".strip()
                if not name or name == " ":
                    name = "Unknown"

                # Estrazione della squadra corretta (annidata dentro "player" -> "team")
                team_obj = person.get("team", {})
                team_code = team_obj.get("code", "") if isinstance(team_obj, dict) else ""
                
                # Fallback di sicurezza nel caso non sia lì
                if not team_code:
                    t_fallback = p.get("team", {})
                    if isinstance(t_fallback, dict):
                        team_code = t_fallback.get("code", "")

                player_entry = {
                    "Player": name,
                    "Team": team_code,
                    "GP": p.get("gamesPlayed", 0),
                    "MIN": p.get("minutesPlayed", 0),
                    "PTS": p.get("pointsScored", 0),
                    "REB": p.get("totalRebounds", 0),
                    "AST": p.get("assists", 0),
                    "STL": p.get("steals", 0),
                    "BLK": p.get("blocks", 0),
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
