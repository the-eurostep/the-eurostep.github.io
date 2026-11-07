import json
import datetime
import requests

def parse_box_score(game_code):
    """Funzione di diagnostica e recupero per i box score"""
    boxscore = {"homePlayers": [], "awayPlayers": []}
    
    # Proviamo l'endpoint ufficiale standard di Eurolega per il boxscore della partita
    url = f"https://live.euroleague.net/api/Boxscore?gamecode={game_code}&seasoncode=E2026"
    print(f"-> Controllo Boxscore per match ID (gamecode): {game_code} (URL: {url})")
    
    try:
        res = requests.get(url, timeout=5)
        print(f"-> Status Code ricevuto: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            # Stampiamo una anteprima nei log per capire come è fatto il JSON
            print(f"-> Dati ricevuti (anteprima): {str(data)[:250]}")
            
            # Qui inseriremo la mappatura non appena vediamo la struttura nei log
        else:
            print(f"-> Errore HTTP dal server Eurolega: {res.status_code}")
            
    except Exception as e:
        print(f"-> Eccezione riscontrata durante la richiesta: {e}")
        
    return boxscore

def fetch_euroleague_games():
    print("=== Avvio aggiornamento calendario e risultati Eurolega ===")
    
    season_data = {
        "currentRound": 10,
        "rounds": {}
    }

    today = datetime.date.today()

    for round_num in range(1, 39):
        matches_in_round = []
        url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2026/games?teamCode=&phaseTypeCode=RS&roundNumber={round_num}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                games = data.get("data", [])
                
                for g in games:
                    raw_date = g.get("date", "")
                    match_datetime = datetime.datetime.min
                    match_date_str = ""
                    match_time_str = "20:30"
                    is_played = False
                    
                    if raw_date:
                        try:
                            match_datetime = datetime.datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                            match_date_str = match_datetime.strftime("%d/%m/%Y")
                            match_time_str = match_datetime.strftime("%H:%M")
                            is_played = match_datetime.date() < today or g.get("status") == "result"
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
                    
                    if home_score is None: home_score = 0
                    if away_score is None: away_score = 0

                    game_code = g.get("code", "")

                    boxscore_data = None
                    if is_played and game_code:
                        boxscore_data = parse_box_score(game_code)

                    matches_in_round.append({
                        "datetime_obj": match_datetime,
                        "date": match_date_str,
                        "time": f"{match_time_str} CET",
                        "status": "played" if is_played and (home_score > 0 or away_score > 0) else "upcoming",
                        "homeTeam": home_team_name,
                        "homeLogo": home_logo,
                        "homeScore": home_score,
                        "awayTeam": away_team_name,
                        "awayLogo": away_logo,
                        "awayScore": away_score,
                        "boxscore": boxscore_data
                    })
                
                # Ordinamento cronologico corretto
                matches_in_round.sort(key=lambda x: x["datetime_obj"])
                
                for m in matches_in_round:
                    del m["datetime_obj"]

            else:
                print(f"Errore HTTP {response.status_code} per il round {round_num}")
        except Exception as e:
            print(f"Errore di connessione per il round {round_num}: {e}")

        season_data["rounds"][str(round_num)] = matches_in_round

    with open("euroleague-games-data.json", "w", encoding="utf-8") as f:
        json.dump(season_data, f, ensure_ascii=False, indent=4)
    
    print("=== File euroleague-games-data.json salvato con successo! ===")

if __name__ == "__main__":
    fetch_euroleague_games()
