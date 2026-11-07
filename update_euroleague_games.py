import json
import datetime
import requests

def fetch_euroleague_games():
    print("Aggiornamento del calendario e dei risultati Eurolega tramite API ufficiale...")
    
    season_data = {
        "currentRound": 10, # Aggiornato al round attuale (Novembre 2026)
        "rounds": {}
    }

    today = datetime.date.today()

    # Iteriamo su tutti i 38 round della regular season
    for round_num in range(1, 39):
        matches_in_round = []
        url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2026/games?teamCode=&phaseTypeCode=RS&roundNumber={round_num}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                games = data.get("data", [])
                
                for g in games:
                    # Estrazione data e formattazione in stile europeo (DD/MM/YYYY)
                    raw_date = g.get("date", "")
                    match_date_str = ""
                    match_time_str = "20:30"
                    is_played = False
                    
                    if raw_date:
                        try:
                            # Esempio formato API: 2026-11-06T19:45:00.000Z
                            dt = datetime.datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                            match_date_str = dt.strftime("%d/%m/%Y")
                            match_time_str = dt.strftime("%H:%M")
                            is_played = dt.date() < today or g.get("status") == "result"
                        except Exception:
                            match_date_str = raw_date[:10]

                    home = g.get("home", {})
                    away = g.get("away", {})
                    
                    home_team_name = home.get("name", "Home Team")
                    away_team_name = away.get("name", "Away Team")
                    
                    home_logo = home.get("imageUrls", {}).get("crest", "the eurostep rounded.png")
                    away_logo = away.get("imageUrls", {}).get("crest", "the eurostep rounded.png")
                    
                    home_score = home.get("score", 0) if is_played else 0
                    away_score = away.get("score", 0) if is_played else 0
                    
                    # Se lo score è null (partite future o non iniziate)
                    if home_score is None: home_score = 0
                    if away_score is None: away_score = 0

                    matches_in_round.append({
                        "date": match_date_str,
                        "time": f"{match_time_str} CET",
                        "status": "played" if is_played and (home_score > 0 or away_score > 0) else "upcoming",
                        "homeTeam": home_team_name,
                        "homeLogo": home_logo,
                        "homeScore": home_score,
                        "awayTeam": away_team_name,
                        "awayLogo": away_logo,
                        "awayScore": away_score,
                        "boxscore": None # Lo collegheremo nella Fase 2
                    })
            else:
                print(f"Errore HTTP {response.status_code} per il round {round_num}")
        except Exception as e:
            print(f"Errore di connessione per il round {round_num}: {e}")

        season_data["rounds"][str(round_num)] = matches_in_round

    # Salvataggio del file JSON finale per il sito
    with open("euroleague-games-data.json", "w", encoding="utf-8") as f:
        json.dump(season_data, f, ensure_ascii=False, indent=4)
    
    print("File euroleague-games-data.json generato con successo dai feed ufficiali!")

if __name
