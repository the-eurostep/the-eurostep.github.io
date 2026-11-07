import json
import pandas as pd

def fetch_nba_data():
    print("Scaricamento delle statistiche NBA da Basketball Reference...")
    
    # URL delle pagine delle statistiche per la stagione corrente (2026-27)
    players_url = "https://www.basketball-reference.com/leagues/NBA_2027_per_game.html"
    teams_url = "https://www.basketball-reference.com/leagues/NBA_2027.html"
    
    players_data = []
    teams_data = []
    
    try:
        # --- 1. ESTRAZIONE GIOCATORI ---
        dfs_players = pd.read_html(players_url)
        df_p = dfs_players[0]
        
        # Pulisci le righe ripetite delle intestazioni che Basketball Reference inserisce a metà tabella
        df_p = df_p[df_p['Player'] != 'Player']
        df_p = df_p.dropna(subset=['Player', 'Team'])
        
        # Mappatura delle sigle delle squadre a 3 lettere in maiuscolo
        team_mapping = {
            'ATL': 'ATL', 'BOS': 'BOS', 'BRK': 'BRK', 'CHO': 'CHO', 'CHI': 'CHI',
            'CLE': 'CLE', 'DAL': 'DAL', 'DEN': 'DEN', 'DET': 'DET', 'GSW': 'GSW',
            'HOU': 'HOU', 'IND': 'IND', 'LAC': 'LAC', 'LAL': 'LAL', 'MEM': 'MEM',
            'MIA': 'MIA', 'MIL': 'MIL', 'MIN': 'MIN', 'NOP': 'NOP', 'NYK': 'NYK',
            'OKC': 'OKC', 'ORL': 'ORL', 'PHI': 'PHI', 'PHO': 'PHO', 'POR': 'POR',
            'SAC': 'SAC', 'SAS': 'SAS', 'TOR': 'TOR', 'UTA': 'UTA', 'WAS': 'WAS',
            'TOT': 'TOT'
        }

        for _, row in df_p.iterrows():
            # Nome giocatore in maiuscolo o pulito
            p_name = str(row.get('Player', '')).strip().upper()
            p_team = str(row.get('Team', '')).strip().upper()
            p_team_abbr = team_mapping.get(p_team, p_team)
            
            def safe_float(val):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0.0

            player_obj = {
                "Player": p_name,
                "Team": p_team_abbr,
                "GP": int(safe_float(row.get('G', 0))),
                "MIN": safe_float(row.get('MP', 0)),
                "PTS": safe_float(row.get('PTS', 0)),
                "OREB": safe_float(row.get('ORB', 0)),
                "DREB": safe_float(row.get('DRB', 0)),
                "REB": safe_float(row.get('TRB', 0)),
                "AST": safe_float(row.get('AST', 0)),
                "STL": safe_float(row.get('STL', 0)),
                "BLK": safe_float(row.get('BLK', 0)),
                "FGM": safe_float(row.get('FG', 0)),
                "FGA": safe_float(row.get('FGA', 0)),
                "3PM": safe_float(row.get('3P', 0)),
                "3PA": safe_float(row.get('3PA', 0)),
                "FTM": safe_float(row.get('FT', 0)),
                "FTA": safe_float(row.get('FTA', 0)),
                "PF": safe_float(row.get('PF', 0)),
                "TO": safe_float(row.get('TOV', 0)),
                "PLUS_MINUS": 0.0 # Valore di default se non presente nella tabella base
            }
            players_data.append(player_obj)
            
    except Exception as e:
        print(f"Errore nel parsing dei giocatori: {e}")

    try:
        # --- 2. ESTRAZIONE SQUADRE ---
        dfs_teams = pd.read_html(teams_url)
        # Cerchiamo la tabella delle medie squadra o dei ratings
        df_t = None
        for df in dfs_teams:
            if 'Team' in df.columns and ('PTS' in df.columns or 'ORtg' in df.columns):
                df_t = df
                break
        
        if df_t is not None:
            for _, row in df_t.iterrows():
                t_name = str(row.get('Team', '')).strip().upper()
                if not t_name or 'LEAGUE' in t_name:
                    continue
                
                team_obj = {
                    "Team": t_name,
                    "GP": int(safe_float(row.get('G', row.get('MP', 0)))), # Gestione flessibile delle colonne
                    "PTS": safe_float(row.get('PTS', 0)),
                    "OREB": safe_float(row.get('ORB', 0)),
                    "DREB": safe_float(row.get('DRB', 0)),
                    "REB": safe_float(row.get('TRB', row.get('REB', 0))),
                    "AST": safe_float(row.get('AST', 0)),
                    "STL": safe_float(row.get('STL', 0)),
                    "BLK": safe_float(row.get('BLK', 0)),
                    "FGM": safe_float(row.get('FG', 0)),
                    "FGA": safe_float(row.get('FGA', 0)),
                    "3PM": safe_float(row.get('3P', 0)),
                    "3PA": safe_float(row.get('3PA', 0)),
                    "FTM": safe_float(row.get('FT', 0)),
                    "FTA": safe_float(row.get('FTA', 0)),
                    "PF": safe_float(row.get('PF', 0)),
                    "TO": safe_float(row.get('TOV', 0))
                }
                teams_data.append(team_obj)
    except Exception as e:
        print(f"Errore nel parsing delle squadre: {e}")

    # Struttura finale JSON
    final_output = {
        "players": players_data,
        "teams": teams_data
    }

    with open("nba-data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
    
    print("File nba-data.json generato con successo!")

if __name__ == "__main__":
    fetch_nba_data()
