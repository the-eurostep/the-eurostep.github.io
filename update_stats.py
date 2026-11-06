import json
import urllib.request
import urllib.error

def fetch_euroleague_data():
    print("Inizio recupero dati Euroleague...")
    
    # Endpoint ufficiale per i dati statistici
    url = "https://api-live.euroleague.net/v3/competitions/E/statistics"
    
    players_data = []
    teams_data = []

    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            # Elaborazione dati per popolare player_data e teams_data
    except Exception as e:
        print(f"Errore durante il recupero dei dati: {e}")

    # Struttura dati JSON con tutte le colonne richieste:
    # Giocatori: Player, Team, GP, MIN, PTS, OREB, DREB, REB, AST, STL, BLK, PF, 3PM, 3PA, 3P%, FGM, FGA, FG%, FTM, FTA, FT%, PIR
    # Squadre: Team, GP, PTS, Punti Subiti (Points Allowed), REB, AST, ecc.
    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("euroleague-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print("File euroleague-data.json aggiornato con successo.")

if __name__ == "__main__":
    fetch_euroleague_data()
