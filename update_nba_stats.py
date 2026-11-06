import json
import urllib.request
import urllib.error

TEAM_FULL_NAMES = {
    "ATL": "ATLANTA HAWKS", "BOS": "BOSTON CELTICS", "BKN": "BROOKLYN NETS",
    "CHA": "CHARLOTTE HORNETS", "CHI": "CHICAGO BULLS", "CLE": "CLEVELAND CAVALIERS",
    "DAL": "DALLAS MAVERICKS", "DEN": "DENVER NUGGETS", "DET": "DETROIT PISTONS",
    "GSW": "GOLDEN STATE WARRIORS", "HOU": "HOUSTON ROCKETS", "IND": "INDIANA PACERS",
    "LAC": "LA CLIPPERS", "LAL": "LOS ANGELES LAKERS", "MEM": "MEMPHIS GRIZZLIES",
    "MIA": "MIAMI HEAT", "MIL": "MILWAUKEE BUCKS", "MIN": "MINNESOTA TIMBERWOLVES",
    "NOP": "NEW ORLEANS PELICANS", "NYK": "NEW YORK KNICKS", "OKC": "OKLAHOMA CITY THUNDER",
    "ORL": "ORLANDO MAGIC", "PHI": "PHILADELPHIA 76ERS", "PHX": "PHOENIX SUNS",
    "POR": "PORTLAND TRAIL BLAZERS", "SAC": "SACRAMENTO KINGS", "SAS": "SAN ANTONIO SPURS",
    "TOR": "TORONTO RAPTORS", "UTA": "UTAH JAZZ", "WAS": "WASHINGTON WIZARDS"
}

def fetch_nba_data_direct():
    print("Inizio recupero dati ufficiali NBA tramite endpoint diretto...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com'
    }

    players_data = []
    teams_data = []

    # Endpoint ufficiale JSON della NBA per le statistiche tradizionali dei giocatori (Per Game)
    players_url = "https://stats.nba.com/stats/leaguedashplayerstats?PerMode=PerGame&Season=2025-26&SeasonType=Regular%20Season"
    
    try:
        print("Scaricamento Player Stats da stats.nba.com...")
        req = urllib.request.Request(players_url, headers=headers)
        # Timeout aumentato a 60 secondi per evitare blocchi
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_data = json.loads(response.read().decode('utf-8'))
            result_sets = raw_data.get('resultSets', [])
            if result_sets:
                headers_list = result_sets[0].get('headers', [])
                rows = result_sets[0].get('rowSet', [])
                
                h_idx = {h: i for i, h in enumerate(headers_list)}
                
                for row in rows:
                    team_abb = row[h_idx.get('TEAM_ABBREVIATION', 0)] or ''
                    fgm = row[h_idx.get('FGM', 0)] or 0
                    fga = row[h_idx.get('FGA', 0)] or 0
                    fg_pct = row[h_idx.get('FG_PCT', 0)] or 0
                    
                    fg3m = row[h_idx.get('FG3M', 0)] or 0
                    fg3a = row[h_idx.get('FG3A', 0)] or 0
                    fg3_pct = row[h_idx.get('FG3_PCT', 0)] or 0

                    ftm = row[h_idx.get('FTM', 0)] or 0
                    fta = row[h_idx.get('FTA', 0)] or 0
                    ft_pct = row[h_idx.get('FT_PCT', 0)] or 0

                    players_data.append({
                        "Player": row[h_idx.get('PLAYER_NAME', 0)],
                        "Team": team_abb,
                        "GP": row[h_idx.get('GP', 0)] or 0,
                        "MIN": round(row[h_idx.get('MIN', 0)] or 0, 1),
                        "PTS": round(row[h_idx.get('PTS', 0)] or 0, 1),
                        "OREB": round(row[h_idx.get('OREB', 0)] or 0, 1),
                        "DREB": round(row[h_idx.get('DREB', 0)] or 0, 1),
                        "REB": round(row[h_idx.get('REB', 0)] or 0, 1),
                        "AST": round(row[h_idx.get('AST', 0)] or 0, 1),
                        "STL": round(row[h_idx.get('STL', 0)] or 0, 1),
                        "BLK": round(row[h_idx.get('BLK', 0)] or 0, 1),
                        "PF": round(row[h_idx.get('PF', 0)] or 0, 1),
                        "FGM": round(fgm, 1),
                        "FGA": round(fga, 1),
                        "FG%": f"{round(fg_pct * 100, 1)}%",
                        "3PM": round(fg3m, 1),
                        "3PA": round(fg3a, 1),
                        "3P%": f"{round(fg3_pct * 100, 1)}%",
                        "FTM": round(ftm, 1),
                        "FTA": round(fta, 1),
                        "FT%": f"{round(ft_pct * 100, 1)}%",
                        "+/-": round(row[h_idx.get('PLUS_MINUS', 0)] or 0, 1)
                    })
        print(f"Scaricati con successo {len(players_data)} giocatori.")
    except Exception as e:
        print(f"Errore scaricamento giocatori: {e}")

    # Endpoint ufficiale JSON della NBA per le statistiche tradizionali delle squadre (Per Game)
    teams_url = "https://stats.nba.com/stats/leaguedashteamstats?PerMode=PerGame&Season=2025-26&SeasonType=Regular%20Season"
    
    try:
        print("Scaricamento Team Stats da stats.nba.com...")
        req_t = urllib.request.Request(teams_url, headers=headers)
        with urllib.request.urlopen(req_t, timeout=60) as response:
            raw_t_data = json.loads(response.read().decode('utf-8'))
            t_result_sets = raw_t_data.get('resultSets', [])
            if t_result_sets:
                t_headers_list = t_result_sets[0].get('headers', [])
                t_rows = t_result_sets[0].get('rowSet', [])
                
                t_h_idx = {h: i for i, h in enumerate(t_headers_list)}
                
                for row in t_rows:
                    raw_team_name = str(row[t_h_idx.get('TEAM_NAME', 0)]).upper()
                    team_abb = row[t_h_idx.get('TEAM_ABBREVIATION', 0)] or ''
                    full_name = TEAM_FULL_NAMES.get(team_abb, raw_team_name)

                    fgm = row[t_h_idx.get('FGM', 0)] or 0
                    fga = row[t_h_idx.get('FGA', 0)] or 0
                    fg_pct = row[t_h_idx.get('FG_PCT', 0)] or 0
                    
                    fg3m = row[t_h_idx.get('FG3M', 0)] or 0
                    fg3a = row[t_h_idx.get('FG3A', 0)] or 0
                    fg3_pct = row[t_h_idx.get('FG3_PCT', 0)] or 0

                    ftm = row[t_h_idx.get('FTM', 0)] or 0
                    fta = row[t_h_idx.get('FTA', 0)] or 0
                    ft_pct = row[t_h_idx.get('FT_PCT', 0)] or 0

                    teams_data.append({
                        "Team": full_name,
                        "GP": row[t_h_idx.get('GP', 0)] or 0,
                        "PTS": round(row[t_h_idx.get('PTS', 0)] or 0, 1),
                        "OREB": round(row[t_h_idx.get('OREB', 0)] or 0, 1),
                        "DREB": round(row[t_h_idx.get('DREB', 0)] or 0, 1),
                        "REB": round(row[t_h_idx.get('REB', 0)] or 0, 1),
                        "AST": round(row[t_h_idx.get('AST', 0)] or 0, 1),
                        "STL": round(row[t_h_idx.get('STL', 0)] or 0, 1),
                        "BLK": round(row[t_h_idx.get('BLK', 0)] or 0, 1),
                        "PF": round(row[t_h_idx.get('PF', 0)] or 0, 1),
                        "FGM": round(fgm, 1),
                        "FGA": round(fga, 1),
                        "FG%": f"{round(fg_pct * 100, 1)}%",
                        "3PM": round(fg3m, 1),
                        "3PA": round(fg3a, 1),
                        "3P%": f"{round(fg3_pct * 100, 1)}%",
                        "FTM": round(ftm, 1),
                        "FTA": round(fta, 1),
                        "FT%": f"{round(ft_pct * 100, 1)}%"
                    })
        print(f"Scaricate con successo {len(teams_data)} squadre.")
    except Exception as e:
        print(f"Errore scaricamento squadre: {e}")

    # Salvataggio nel file JSON finale
    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("nba-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"Salvataggio completato: {len(players_data)} giocatori e {len(teams_data)} squadre scritti in nba-data.json.")

if __name__ == "__main__":
    fetch_nba_data_direct()
