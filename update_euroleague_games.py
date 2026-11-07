import json
import datetime
import requests

def parse_box_score(game_code, home_tla, away_tla):
    """Funzione per recuperare i tabellini dei giocatori dai feed live dell'Eurolega"""
    boxscore = {"homePlayers": [], "awayPlayers": []}
    
    for tla, team_key in [(home_tla, "homePlayers"), (away_tla, "awayPlayers")]:
        if not tla:
            continue
        url = f"https://live.euroleague.net/api/Players?gamecode={game_code}&seasoncode=E2026&disp=&equipo={tla}&temp=E2026"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                # L'API restituisce la lista dei giocatori della squadra
                players_list = data if isinstance(data, list) else data.get("Players", [])
                
                formatted_players = []
                for p in players_list:
                    formatted_players.append({
                        "name": p.get("Player", p.get("Name", "Player")),
                        "min": p.get("Min", "00:00"),
                        "pts": p.get("Points", p.get("PTS", 0)),
                        "oreb": p.get("OffRebounds", 0),
                        "dreb": p.get("DefRebounds", 0),
                        "reb": p.get("TotalRebounds", p.get("REB", 0)),
                        "ast": p.get("Assist", p.get("AST", 0)),
                        "stl": p.get("Steals", p.get("STL", 0)),
                        "blk": p.get("Turnovers", p.get("BLK", 0)), # o stoppate se presenti
                        "tpm2": p.get("FieldGoalsMade2", 0),
                        "tpa2": p.get("FieldGoalsAttempted2", 0),
                        "tp_pct2": str(p.get("FieldGoalsPercentage2", ".000")),
                        "tpm3": p.get("FieldGoalsMade3", 0),
                        "tpa3": p.get("FieldGoalsAttempted3", 0),
                        "tp_pct3": str(p.get("FieldGoalsPercentage3", ".000")),
                        "ftm": p.get("FreeThrowsMade", 0),
                        "fta": p.get("FreeThrowsAttempted", 0),
                        "ft_pct": str(p.get("FreeThrowsPercentage", ".000")),
                        "to": p.get("Turnovers", 0),
                        "pf": p.get("FoulsCommited", 0),
                        "pir": p.get("Valuation", p.get("PIR", 0)),
                        "plusMinus": str(p.get("PlusMinus", 0))
                    })
                boxscore[team_key] = formatted_players
        except Exception as e:
            print(f"Errore recupero box score per {tla} (Match {game_code}): {e}")
            
    return boxscore

def fetch_euroleague_games():
    print("Aggiornamento del calendario, risultati e ordinamento cronologico Eurolega...")
    
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
                    home_tla = home.get("tla", "")
                    away_tla = away.get("tla", "")
                    
                    home_logo = home.get("imageUrls", {}).get("crest", "the eurostep rounded.png")
                    away_logo = away.get("imageUrls", {}).get("crest", "the eurostep rounded.png")
                    
                    home_score = home.get("score", 0) if is_played else 0
                    away_score = away.get("score", 0) if is_played else 0
                    
                    if home_score is None: home_score = 0
                    if away_score is None: away_score = 0

                    # Codice partita per i box score (es. "99" o estratto dall'id)
                    game_code = g.get("code", "")

                    # Recupero box score se la partita è giocata
                    boxscore_data = None
                    if is_played and game_code:
                        boxscore_data = parse_box_score(game_code, home_tla, away_tla)

                    matches_in_round.append({
                        "datetime_obj": match_datetime, # Usato per ordinare
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
                
                # Ordinamento cronologico corretto (dalla prima alla più tardi nel round)
                matches_in_round.sort(key=lambda x: x["datetime_obj"])
                
                # Rimuoviamo l'oggetto datetime temporaneo prima di salvare nel JSON
                for m in matches_in_round:
                    del m["datetime_obj"]

            else:
                print(f"Errore HTTP {response.status_code} per il round {round_num}")
        except Exception as e:
            print(f"Errore di connessione per il round {round_num}: {e}")

        season_data["rounds"][str(round_num)] = matches_in_round

    with open("euroleague-games-data.json", "w", encoding="utf-8") as f:
        json.dump(season_data, f, ensure_ascii=False, indent=4)
    
    print("File euroleague-games-data.json ordinato e aggiornato con successo!")

if __name__ == "__main__":
    fetch_euroleague_games()
