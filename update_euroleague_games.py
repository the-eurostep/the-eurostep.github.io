import json
import datetime
import time
import requests

def parse_box_score(game_code):
    """Estrae e mappa con precisione millimetrica i tabellini dei giocatori usando le chiavi ufficiali Euroleague"""
    boxscore = {"homePlayers": [], "awayPlayers": []}
    
    url = f"https://live.euroleague.net/api/Boxscore?gamecode={game_code}&seasoncode=E2026"
    try:
        # Pausa per evitare il blocco HTTP 429 (Too Many Requests)
        time.sleep(0.4)
        res = requests.get(url, timeout=6)
        
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                stats = data.get("Stats", [])
                if isinstance(stats, list) and len(stats) >= 2:
                    boxscore["homePlayers"] = format_players_list(stats[0].get("PlayersStats", []))
                    boxscore["awayPlayers"] = format_players_list(stats[1].get("PlayersStats", []))
        else:
            print(f"Errore HTTP {res.status_code} per boxscore match {game_code}")
    except Exception as e:
        print(f"Errore recupero box score (Match {game_code}): {e}")
        
    return boxscore

def format_players_list(players_raw):
    """Mappa i campi esatti del JSON ufficiale dell'Eurolega"""
    formatted = []
    if not isinstance(players_raw, list):
        return formatted

    for p in players_raw:
        # Estrazione tiri e calcolo percentuali sicure
        fgm2 = p.get("FieldGoalsMade2", 0) or 0
        fga2 = p.get("FieldGoalsAttempted2", 0) or 0
        pct2 = f"{round((fgm2 / fga2) * 100, 1)}%" if fga2 > 0 else "0.0%"

        fgm3 = p.get("FieldGoalsMade3", 0) or 0
        fga3 = p.get("FieldGoalsAttempted3", 0) or 0
        pct3 = f"{round((fgm3 / fga3) * 100, 1)}%" if fga3 > 0 else "0.0%"

        ftm = p.get("FreeThrowsMade", 0) or 0
        fta = p.get("FreeThrowsAttempted", 0) or 0
        pct_ft = f"{round((ftm / fta) * 100, 1)}%" if fta > 0 else "0.0%"

        formatted.append({
            "name": p.get("Player", "Player").strip(),
            "min": p.get("Minutes", "00:00"),
            "pts": p.get("Points", 0),
            "oreb": p.get("OffensiveRebounds", 0),
            "dreb": p.get("DefensiveRebounds", 0),
            "reb": p.get("TotalRebounds", 0),
            "ast": p.get("Assistances", 0),
            "stl": p.get("Steals", 0),
            "blk": p.get("BlocksFavour", 0),
            "tpm2": fgm2,
            "tpa2": fga2,
            "tp_pct2": pct2,
            "tpm3": fgm3,
            "tpa3": fga3,
            "tp_pct3": pct3,
            "ftm": ftm,
            "fta": fta,
            "ft_pct": pct_ft,
            "to": p.get("Turnovers", 0),
            "pf": p.get("FoulsCommited", 0),
            "pir": p.get("Valuation", 0),
            "plusMinus": str(p.get("Plusminus", 0))
        })
    return formatted

def fetch_euroleague_games():
    print("=== Avvio aggiornamento calendario, risultati e box score Eurolega ===")
    
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
