import json
import urllib.request
import urllib.error

def fetch_euroleague_data():
    print("Inizio recupero dati Euroleague...")
    
    # URL ufficiale estratto dai flussi dell'Eurolega
    players_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/players/traditional?seasonMode=Single&limit=1000&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    
    players_data = []
    teams_data = []

    # Intestazioni per simulare un browser reale ed evitare qualsiasi blocco anti-bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }

    try:
        # Recupero dati Giocatori
        req_players = urllib.request.Request(players_url, headers=headers)
        with urllib.request.urlopen(req_players) as response:
            raw_data = json.loads(response.read().decode('utf-8'))
            
            # L'API restituisce solitamente una lista o un dizionario contenente i dati
            items = raw_data if isinstance(raw_data, list) else raw_data.get('data', raw_data.get('players', []))
            
            for p in items:
                # Estrazione sicura dei campi richiesti (inclusi PIR, PTS, rimbalzi, ecc.)
                player_entry = {
                    "Player": p.get("playerName", p.get("name", "Unknown")),
                    "Team": p.get("teamCode", p.get("team", {}).get("code", "")),
                    "GP": p.get("gamesPlayed", p.get("gp", 0)),
                    "MIN": p.get("minutes", p.get("min", 0)),
                    "PTS": p.get("points", p.get("pts", 0)),
                    "REB": p.get("totalRebounds", p.get("reb", 0)),
                    "AST": p.get("assists", p.get("ast", 0)),
                    "STL": p.get("steals", p.get("stl", 0)),
                    "BLK": p.get("blocks", p.get("blk", 0)),
                    "PIR": p.get("valuation", p.get("pir", p.get("indexRating", 0)))
                }
                players_data.append(player_entry)
                
    except Exception as e:
        print(f"Errore durante il recupero dei dati giocatori: {e}")

    # Struttura finale pulita per il tuo sito The Eurostep
    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    # Scrittura del file JSON finale letto dal sito
    with open("euroleague-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print(f"File euroleague-data.json generato con successo! {len(players_data)} giocatori caricati.")

if __name__ == "__main__":
    fetch_euroleague_data()
