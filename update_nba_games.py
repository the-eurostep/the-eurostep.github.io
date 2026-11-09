import json
import datetime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
import requests

def parse_shooting_stat(stat_str):
    if "-" in stat_str:
        parts = stat_str.split("-")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            made = int(parts[0])
            att = int(parts[1])
            pct = f"{(made / att * 100):.1f}%" if att > 0 else "0.0%"
            return made, att, pct
    return 0, 0, "0.0%"

def parse_nba_box_score(event_id):
    boxscore = {"homePlayers": [], "awayPlayers": []}
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={event_id}"
    try:
        time.sleep(0.2)
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            boxscore_data = data.get("boxscore", {})
            teams_stats = boxscore_data.get("players", [])
            
            if len(teams_stats) >= 2:
                away_data = teams_stats[0].get("statistics", [{}])[0].get("athletes", [])
                home_data = teams_stats[1].get("statistics", [{}])[0].get("athletes", [])
                
                boxscore["awayPlayers"] = format_nba_players(away_data)
                boxscore["homePlayers"] = format_nba_players(home_data)
    except Exception as e:
        print(f"Errore recupero box score NBA (Match {event_id}): {e}")
    return boxscore

def format_nba_players(athletes_raw):
    formatted = []
    for ath in athletes_raw:
        stats = ath.get("stats", [])
        name = ath.get("athlete", {}).get("displayName", "Player")
        
        min_val = stats[0] if len(stats) > 0 else "0"
        pts = int(stats[1]) if len(stats) > 1 and stats[1].isdigit() else 0
        
        fgm, fga, fg_pct = parse_shooting_stat(stats[2] if len(stats) > 2 else "0-0")
        tpm3, tpa3, tp_pct3 = parse_shooting_stat(stats[3] if len(stats) > 3 else "0-0")
        ftm, fta, ft_pct = parse_shooting_stat(stats[4] if len(stats) > 4 else "0-0")
        
        reb = int(stats[5]) if len(stats) > 5 and stats[5].isdigit() else 0
        ast = int(stats[6]) if len(stats) > 6 and stats[6].isdigit() else 0
        to = int(stats[7]) if len(stats) > 7 and stats[7].isdigit() else 0
        stl = int(stats[8]) if len(stats) > 8 and stats[8].isdigit() else 0
        blk = int(stats[9]) if len(stats) > 9 and stats[9].isdigit() else 0
        oreb = int(stats[10]) if len(stats) > 10 and stats[10].isdigit() else 0
        dreb = int(stats[11]) if len(stats) > 11 and stats[11].isdigit() else 0
        pf = int(stats[12]) if len(stats) > 12 and stats[12].isdigit() else 0
        plus_minus = stats[13] if len(stats) > 13 else "0"
        
        formatted.append({
            "name": name, "min": min_val, "fgm": fgm, "fga": fga, "fg_pct": fg_pct,
            "tpm3": tpm3, "tpa3": tpa3, "tp_pct3": tp_pct3, "ftm": ftm, "fta": fta,
            "ft_pct": ft_pct, "oreb": oreb, "dreb": dreb, "reb": reb, "ast": ast,
            "stl": stl, "blk": blk, "to": to, "pf": pf, "pts": pts, "plusMinus": plus_minus
        })
    return formatted

def fetch_nba_games():
    print("=== Avvio aggiornamento calendario NBA (Multi-giorno & Doppi orari) ==pss")
    season_data = {"dates": {}}

    # Generiamo un range di date da 5 giorni fa a 25 giorni nel futuro per coprire l'intera settimana corrente e dintorni
    today = datetime.now(ZoneInfo("America/New_York")).date()
    start_date = today - timedelta(days=5)
    end_date = today + timedelta(days=25)
    
    current_d = start_date
    while current_d <= end_date:
        date_param = current_d.strftime("%Y%m%d")
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_param}"
        
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                events = data.get("events", [])
                
                for ev in events:
                    event_id = ev.get("id")
                    raw_date = ev.get("date", "")
                    
                    if not raw_date:
                        continue
                    
                    utc_dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                    
                    # Data solare americana (US Eastern)
                    us_dt = utc_dt.astimezone(ZoneInfo("America/New_York"))
                    date_str = us_dt.strftime("%Y-%m-%d")
                    
                    # Orari formattati compatti: ET (americano) e CET (europeo)
                    et_time = us_dt.strftime("%H:%M") + " ET"
                    cet_dt = utc_dt.astimezone(ZoneInfo("Europe/Rome"))
                    cet_time = cet_dt.strftime("%H:%M") + " CET"
                    display_time = f"{et_time} / {cet_time}"
                    
                    competitions = ev.get("competitions", [{}])[0]
                    competitors = competitions.get("competitors", [])
                    
                    home_team, away_team = {}, {}
                    for comp in competitors:
                        if comp.get("homeAway") == "home": home_team = comp
                        else: away_team = comp
                    
                    home_name = home_team.get("team", {}).get("displayName", "Home")
                    away_name = away_team.get("team", {}).get("displayName", "Away")
                    home_logo = home_team.get("team", {}).get("logo", "the eurostep rounded.png")
                    away_logo = away_team.get("team", {}).get("logo", "the eurostep rounded.png")
                    
                    status_type = competitions.get("status", {}).get("type", {}).get("name", "")
                    is_played = status_type == "STATUS_FINAL"
                    
                    home_score = int(home_team.get("score", 0)) if is_played else 0
                    away_score = int(away_team.get("score", 0)) if is_played else 0
                    
                    boxscore = parse_nba_box_score(event_id) if (is_played and event_id) else None
                    
                    if date_str not in season_data["dates"]:
                        season_data["dates"][date_str] = []
                    
                    # Evitiamo duplicati se una partita viene trovata su più chiamate di data
                    if not any(g["id"] == event_id for g in season_data["dates"][date_str]):
                        season_data["dates"][date_str].append({
                            "id": event_id,
                            "time": display_time,
                            "status": "played" if is_played else "upcoming",
                            "homeTeam": home_name, "homeLogo": home_logo, "homeScore": home_score,
                            "awayTeam": away_name, "awayLogo": away_logo, "awayScore": away_score,
                            "boxscore": boxscore
                        })
        except Exception as e:
            print(f"Errore durante il fetch per la data {date_param}: {e}")
        
        current_d += timedelta(days=1))

    with open("nba-games-data.json", "w", encoding="utf-8") as f:
        json.dump(season_data, f, ensure_ascii=False, indent=4)
    print("=== File nba-games-data.json aggiornato con successo per tutta la stagione! ===")

if __name__ == "__main__":
    fetch_nba_games()
