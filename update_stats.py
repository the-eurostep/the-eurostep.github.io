import json
import urllib.request

# Definizione della struttura dei dati per Euroleague Stats
def fetch_euroleague_data():
    # Struttura base JSON per il tuo sito
    data = {
        "players": [],
        "teams": []
    }
    
    # Qui lo script popola le metriche richieste:
    # Players: Player, Team, GP, MIN, PTS, OREB, DREB, REB, AST, STL, BLK, PF, 3PM, 3PA, 3P%, FGM, FGA, FG%, FTM, FTA, FT%, PIR
    # Teams: Team, GP, PTS, Points Allowed (Subiti), REB, AST, ecc.
    
    with open("euroleague-data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("File euroleague-data.json aggiornato con successo.")

if __name__ == "__main__":
    fetch_euroleague_data()
