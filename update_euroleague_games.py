import json
import datetime

def generate_euroleague_games():
    print("Generazione dei dati per il Game Center Eurolega...")

    # Struttura dati iniziale per i 38 round
    # (Lo script popolerà automaticamente i match, le date, i punteggi e i box score)
    
    season_data = {
        "currentRound": 1, # Verrà aggiornato automaticamente in base alla data odierna
        "rounds": {}
    }

    # Simulazione / Struttura dei 38 round della regular season
    for round_num in range(1, 39):
        matches_in_round = []
        
        # Per ora inseriamo una struttura di esempio per testare la grafica,
        # che poi collegheremo dinamicamente alle API o alle pagine ufficiali dell'Eurolega
        for match_idx in range(1, 10): # 9 partite per round (18 squadre)
            matches_in_round.append({
                "date": "2026-10-15",
                "time": "20:00 CET",
                "status": "upcoming", # o "played" per le partite concluse
                "homeTeam": f"TEAM HOME {match_idx}",
                "homeLogo": "the eurostep rounded.png",
                "homeScore": 0,
                "awayTeam": f"TEAM AWAY {match_idx}",
                "awayLogo": "the eurostep rounded.png",
                "awayScore": 0,
                "boxscore": None
            })
            
        season_data["rounds"][str(round_num)] = matches_in_round

    # Salva il file JSON finale
    with open("euroleague-games-data.json", "w", encoding="utf-8") as f:
        json.dump(season_data, f, ensure_ascii=False, indent=4)
    
    print("File euroleague-games-data.json creato con successo!")

if __name__ == "__main__":
    generate_euroleague_games()
