import json
import time
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats

# Mappa per garantire che i nomi completi delle 30 squadre siano in CAPS LOCK
TEAM_FULL_NAMES = {
    "ATL": "ATLANTA HAWKS",
    "BOS": "BOSTON CELTICS",
    "BKN": "BROOKLYN NETS",
    "CHA": "CHARLOTTE HORNETS",
    "CHI": "CHICAGO BULLS",
    "CLE": "CLEVELAND CAVALIERS",
    "DAL": "DALLAS MAVERICKS",
    "DEN": "DENVER NUGGETS",
    "DET": "DETROIT PISTONS",
    "GSW": "GOLDEN STATE WARRIORS",
    "HOU": "HOUSTON ROCKETS",
    "IND": "INDIANA PACERS",
    "LAC": "LA CLIPPERS",
    "LAL": "LOS ANGELES LAKERS",
    "MEM": "MEMPHIS GRIZZLIES",
    "MIA": "MIAMI HEAT",
    "MIL": "MILWAUKEE BUCKS",
    "MIN": "MINNESOTA TIMBERWOLVES",
    "NOP": "NEW ORLEANS PELICANS",
    "NYK": "NEW YORK KNICKS",
    "OKC": "OKLAHOMA CITY THUNDER",
    "ORL": "ORLANDO MAGIC",
    "PHI": "PHILADELPHIA 76ERS",
    "PHX": "PHOENIX SUNS",
    "POR": "PORTLAND TRAIL BLAZERS",
    "SAC": "SACRAMENTO KINGS",
    "SAS": "SAN ANTONIO SPURS",
    "TOR": "TORONTO RAPTORS",
    "UTA": "UTAH JAZZ",
    "WAS": "WASHINGTON WIZARDS"
}

def fetch_nba_data():
    print("Inizio recupero dati ufficiali NBA da stats.nba.com...")
    
    players_data = []
    teams_data = []

    try:
        # 1. GIOCATORI (Traditional PerGame)
        print("Scaricamento Player Stats...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            per_mode_detailed='PerGame',
            season='2025-26'
        )
        p_dict = player_stats.get_dict()
        p_headers = p_dict['resultSets'][0]['headers']
        p_rows = p_dict['resultSets'][0]['rowSet']

        # Mappatura indici delle colonne
        h_idx_p = {header: idx for idx, header in enumerate(p_headers)}

        for row in p_rows:
            team_abb = row[h_idx_p.get('TEAM_ABBREVIATION', 0)] or ''
            fgm = row[h_idx_p.get('FGM', 0)] or 0
            fga = row[h_idx_p.get('FGA', 0)] or 0
            fg_pct = row[h_idx_p.get('FG_PCT', 0)] or 0
            
            fg3m = row[h_idx_p.get('FG3M', 0)] or 0
            fg3a = row[h_idx_p.get('FG3A', 0)] or 0
            fg3_pct = row[h_idx_p.get('FG3_PCT', 0)] or 0

            ftm = row[h_idx_p.get('FTM', 0)] or 0
            fta = row[h_idx_p.get('FTA', 0)] or 0
            ft_pct = row[h_idx_p.get('FT_PCT', 0)] or 0

            players_data.append({
                "Player": row[h_idx_p.get('PLAYER_NAME', 0)],
                "Team": team_abb,
                "GP": row[h_idx_p.get('GP', 0)] or 0,
                "MIN": round(row[h_idx_p.get('MIN', 0)] or 0, 1),
                "PTS": round(row[h_idx_p.get('PTS', 0)] or 0, 1),
                "OREB": round(row[h_idx_p.get('OREB', 0)] or 0, 1),
                "DREB": round(row[h_idx_p.get('DREB', 0)] or 0, 1),
                "REB": round(row[h_idx_p.get('REB', 0)] or 0, 1),
                "AST": round(row[h_idx_p.get('AST', 0)] or 0, 1),
                "STL": round(row[h_idx_p.get('STL', 0)] or 0, 1),
                "BLK": round(row[h_idx_p.get('BLK', 0)] or 0, 1),
                "PF": round(row[h_idx_p.get('PF', 0)] or 0, 1),
                "FGM": round(fgm, 1),
                "FGA": round(fga, 1),
                "FG%": f"{round(fg_pct * 100, 1)}%",
                "3PM": round(fg3m, 1),
                "3PA": round(fg3a, 1),
                "3P%": f"{round(fg3_pct * 100, 1)}%",
                "FTM": round(ftm, 1),
                "FTA": round(fta, 1),
                "FT%": f"{round(ft_pct * 100, 1)}%",
                "+/-": round(row[h_idx_p.get('PLUS_MINUS', 0)] or 0, 1)
            })

        print(f"Scaricati {len(players_data)} giocatori NBA.")

        # Pausa di sicurezza per rispetto delle API NBA
        time.sleep(2)

        # 2. SQUADRE (Traditional PerGame)
        print("Scaricamento Team Stats...")
        team_stats = leaguedashteamstats.LeagueDashTeamStats(
            per_mode_detailed='PerGame',
            season='2025-26'
        )
        t_dict = team_stats.get_dict()
        t_headers = t_dict['resultSets'][0]['headers']
        t_rows = t_dict['resultSets'][0]['rowSet']

        h_idx_t = {header: idx for idx, header in enumerate(t_headers)}

        for row in t_rows:
            raw_team_name = str(row[h_idx_t.get('TEAM_NAME', 0)]).upper()
            fgm = row[h_idx_t.get('FGM', 0)] or 0
            fga = row[h_idx_t.get('FGA', 0)] or 0
            fg_pct = row[h_idx_t.get('FG_PCT', 0)] or 0
            
            fg3m = row[h_idx_t.get('FG3M', 0)] or 0
            fg3a = row[h_idx_t.get('FG3A', 0)] or 0
            fg3_pct = row[h_idx_t.get('FG3_PCT', 0)] or 0

            ftm = row[h_idx_t.get('FTM', 0)] or 0
            fta = row[h_idx_t.get('FTA', 0)] or 0
            ft_pct = row[h_idx_t.get('FT_PCT', 0)] or 0

            teams_data.append({
                "Team": raw_team_name, # Nome squadra in CAPS LOCK
                "GP": row[h_idx_t.get('GP', 0)] or 0,
                "PTS": round(row[h_idx_t.get('PTS', 0)] or 0, 1),
                "OREB": round(row[h_idx_t.get('OREB', 0)] or 0, 1),
                "DREB": round(row[h_idx_t.get('DREB', 0)] or 0, 1),
                "REB": round(row[h_idx_t.get('REB', 0)] or 0, 1),
                "AST": round(row[h_idx_t.get('AST', 0)] or 0, 1),
                "STL": round(row[h_idx_t.get('STL', 0)] or 0, 1),
                "BLK": round(row[h_idx_t.get('BLK', 0)] or 0, 1),
                "PF": round(row[h_idx_t.get('PF', 0)] or 0, 1),
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

        print(f"Scaricate {len(teams_data)} squadre NBA.")

    except Exception as e:
        print(f"Errore durante l'estrazione dati NBA: {e}")

    # Salvataggio nel file JSON
    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("nba-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print("File nba-data.json salvato con successo!")

if __name__ == "__main__":
    fetch_nba_data()
