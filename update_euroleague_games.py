import json
import datetime
import requests

def parse_box_score(game_code):
    """Funzione per recuperare i tabellini completi dei giocatori dall'API Boxscore dell'Eurolega"""
    boxscore = {"homePlayers": [], "awayPlayers": []}
    
    url = f"https://live.euroleague.net/api/Boxscore?gamecode={game_code}&seasoncode=E2026"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            
            # L'API di solito restituisce i dati suddivisi per squadra (es. ClubA / ClubB o liste di giocatori)
            # Gestiamo le varie strutture possibili restituite dal feed
            teams_data = []
            if isinstance(data, list):
                teams_data = data
            elif isinstance(data, dict):
                # Cerchiamo chiavi comuni nei feed live
                teams_data = data.get("Statistics", data.get("Boxscore", data.get("Players", [])))
                if not teams_data and "Home" in data and "Away" in data:
                    # Se separato in Home e Away
                    return parse_structured_boxscore(data)

            # Se abbiamo una lista di liste (giocatori squadra 1 e squadra 2)
            if len(teams_data) >= 2:
                boxscore["homePlayers"] = format_players_list(teams_data[0])
                boxscore["awayPlayers"] = format_players_list(teams_data[1])
            elif len(teams_data) == 1:
                boxscore["homePlayers"] = format_players_list(teams_data[0])
                
        else:
            print(f"Errore HTTP {res.status_code} per boxscore match {game_code}")
    except Exception as e:
        print(f"Errore recupero box score (Match {game_code}): {e}")
        
    return boxscore

def parse_structured_boxscore(data):
    """Gestione alternativa se il JSON divide direttamente in Home e Away"""
    boxscore = {"homePlayers": [], "awayPlayers": []}
    if "Home" in data:
        boxscore["homePlayers"] = format_players_list(data["Home"])
    if "Away" in data:
        boxscore["awayPlayers"] = format_players_list(data["Away"])
    return boxscore

def format_players_list(players_raw):
    """Formatta la lista dei giocatori mappando correttamente tutte le statistiche"""
    formatted = []
    # Se è un dizionario con dentro una lista di giocatori
    if isinstance(players_raw, dict):
        players_raw = players_raw.get("Players", players_raw.get("队员", []))
        
    if not isinstance(players_raw, list):
        return formatted

    for p in players_raw:
        formatted.append({
            "name": p.get("Player", p.get("Name", p.get("PLAYER", "Player"))),
            "min": p.get("Min", p.get("MIN", "00:00")),
            "pts": p.get("Points", p.get("PTS", 0)),
            "oreb": p.get("OffRebounds", p.get("OREB", 0)),
            "dreb": p.get("DefRebounds", p.get("DREB", 0)),
            "reb": p.get("TotalRebounds", p.get("REB", 0)),
            "ast": p.get("Assist", p.get("AST", 0)),
            "stl": p.get("Steals", p.get("STL", 0)),
            "blk": p.get("BlocksFavour", p.get("BLK", 0)),
            "tpm2": p.get("FieldGoalsMade2", p.get("2PM", 0)),
            "tpa2": p.get("FieldGoalsAttempted2", p.get("2PA", 0)),
            "tp_pct2": str(p.get("FieldGoalsPercentage2", p.get("2P_PCT", ".000"))),
            "tpm3": p.get("FieldGoalsMade3", p.get("3PM", 0)),
            "tpa3": p.get("FieldGoalsAttempted3", p.get("3PA", 0)),
            "tp_pct3": str(p.get("FieldGoalsPercentage3", p.get("3P_PCT", ".000"))),
            "ftm": p.get("FreeThrowsMade", p.get("FTM", 0)),
            "fta": p.get("FreeThrowsAttempted", p.get("FTA", 0)),
            "ft_pct": str(p.get("FreeThrowsPercentage", p.get("FT_PCT", ".000"))),
            "to": p.get("Turnovers", p.get("TO", 0)),
            "pf": p.get("FoulsCommited", p.get("PF", 0)),
            "pir": p.get("Valuation", p.get("PIR", 0)),
            "plusMinus": str(p.get("PlusMinus", p.get("+/-", 0)))
        })
    return formatted

def fetch_euroleague_games():
    print("Aggiornamento del calendario, risultati e box score Eurolega...")
    
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

                    # Recupero box score tramite API Boxscore se la partita è giocata
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
    
    print("File euroleague-games-data.json con box score generato con successo!")

if __name__ == "__main__":
    fetch_euroleague_games()
