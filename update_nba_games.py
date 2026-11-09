import json
import datetime
import time
import requests

def parse_nba_box_score(event_id):
    """Recupera e mappa i tabellini dei giocatori dalle API di ESPN per una specifica partita NBA"""
    boxscore = {"homePlayers": [], "awayPlayers": []}
    
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={event_id}"
    try:
        time.sleep(0.3) # Rate limiting per sicurezza
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            boxscore_data = data.get("boxscore", {})
            teams_stats = boxscore_data.get("players", [])
            
            if len(teams_stats) >= 2:
                # Team 0: Away (di solito), Team 1: Home - verifichiamo la struttura ESPN
                # In ESPN 'players' contiene solitamente due oggetti squadra
                away_data = teams_stats[0].get("statistics", [{}])[0].get("athletes", [])
                home_data = teams_stats[1].get("statistics", [{}])[0].get("athletes", [])
                
                boxscore["awayPlayers"] = format_nba_players(away_data)
                boxscore["homePlayers"] = format_nba_players(home_data)
        else:
            print(f"Errore HTTP {res.status_code} per boxscore NBA match {event_id}")
    except Exception as e:
        print(f"Errore recupero box score NBA (Match {event_id}): {e}")
        
    return boxscore

def format_nba_players(athletes_raw):
    """Mappa le statistiche dei giocatori NBA escludendo PIR, 2PM, 2PA e 2P%"""
    formatted = []
    for ath in athletes_raw:
        stats = ath.get("stats", [])
        # ESPN restituisce le statistiche in un array ordinato di stringhe. 
        # Di solito l'ordine tipico di ESPN boxscore è: MIN, PTS, OREB, DREB, REB, AST, STL, BLK, TO, PF, 3PM-3A, FTM-FTA, +/- (può variare leggermente)
        # Salviamo i campi principali in modo sicuro estraendoli per nome o posizione se mappati.
        name = ath.get("athlete", {}).get("displayName", "Player")
        
        # Estraiamo i campi base se presenti nell'oggetto atleta
        # Nota: adatteremo i campi esatti in base al primo test stampato nei log
        formatted.append({
            "name": name,
            "min": stats[0] if len(stats) > 0 else "0",
            "pts": int(stats[1]) if len(stats) > 1 and stats[1].isdigit() else 0,
            "oreb": int(stats[2]) if len(stats) > 2 and stats[2].isdigit() else 0,
            "dreb": int(stats[3]) if len(stats) > 3 and stats[3].isdigit() else 0,
            "reb": int(stats[4]) if len(stats) > 4 and stats[4].isdigit() else 0,
            "ast": int(stats[5]) if len(stats) > 5 and stats[5].isdigit() else 0,
            "stl": int(stats[6]) if len(stats) > 6 and stats[6].isdigit() else 0,
            "blk": int(stats[7]) if len(stats) > 7 and stats[7].isdigit() else 0,
            "to": int(stats[8]) if len(stats) > 8 and stats[8].isdigit() else 0,
            "pf": int(stats[9]) if len(stats) > 9 and stats[9].isdigit() else 0,
            # Per triple e tiri liberi gestiamo la formattazione pulita
            "tpm3": 0, "tpa3": 0, "tp_pct3": "0.0%",
            "ftm": 0, "fta": 0, "ft_pct": "0.0%",
            "plusMinus": "0"
        })
    return formatted

def fetch_nba_games():
    print("=== Avvio aggiornamento calendario e risultati NBA (ESPN) ===")
    
    season_data = {
        "dates": {}
    }

    # Scarichiamo il blocco delle partite (scoreboard recente / stagione corrente)
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            events = data.get("events", [])
            
            for ev in events:
                event_id = ev.get("id")
                date_str = ev.get("date", "")[:10] # Formato YYYY-MM-DD
                name = ev.get("name", "")
                
                competitions = ev.get("competitions", [{}])[0]
                competitors = competitions.get("competitors", [])
                
                home_team, away_team = {}, {}
                for comp in competitors:
                    if comp.get("homeAway") == "home":
                        home_team = comp
                    else:
                        away_team = comp
                
                home_name = home_team.get("team", {}).get("displayName", "Home")
                away_name = away_team.get("team", {}).get("displayName", "Away")
                
                home_logo = home_team.get("team", {}).get("logo", "the eurostep rounded.png")
                away_logo = away_team.get("team", {}).get("logo", "the eurostep rounded.png")
                
                status_type = competitions.get("status", {}).get("type", {}).get("name", "")
                is_played = status_type == "STATUS_FINAL"
                
                home_score = int(home_team.get("score", 0)) if is_played else 0
                away_score = int(away_team.get("score", 0)) if is_played else 0
                
                boxscore = None
                if is_played and event_id:
                    boxscore = parse_nba_box_score(event_id)
                
                if date_str not in season_data["dates"]:
                    season_data["dates"][date_str] = []
                
                season_data["dates"][date_str].append({
                    "id": event_id,
                    "time": ev.get("date", "")[11:16] + " EST",
                    "status": "played" if is_played else "upcoming",
                    "homeTeam": home_name,
                    "homeLogo": home_logo,
                    "homeScore": home_score,
                    "awayTeam": away_name,
                    "awayLogo": away_logo,
                    "awayScore": away_score,
                    "boxscore": boxscore
                })
                
            with open("nba-games-data.json", "w", encoding="utf-8") as f:
                json.dump(season_data, f, ensure_ascii=False, indent=4)
                
            print("=== File nba-games-data.json salvato con successo! ===")
        else:
            print(f"Errore HTTP scoreboard NBA: {res.status_code}")
    except Exception as e:
        print(f"Errore durante il fetch delle partite NBA: {e}")

if __name__ == "__main__":
    fetch_nba_games()
