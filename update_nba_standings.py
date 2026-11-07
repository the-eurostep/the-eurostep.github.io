import json
import pandas as pd
import requests
from bs4 import BeautifulSoup

def fetch_nba_standings():
    print("Scaricamento delle classifiche NBA da Basketball Reference...")
    url = "https://www.basketball-reference.com/leagues/NBA_2027_standings.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Errore nella richiesta HTTP: status {response.status_code}")
            return

        # Estrazione delle tabelle
        dfs = pd.read_html(response.text)
        
        # In Basketball Reference le tabelle principali delle conference sono solitamente le prime due:
        # Table 0: Eastern Conference | Table 1: Western Conference (oppure viceversa)
        east_df = None
        west_df = None

        for df in dfs:
            cols = [str(c).lower() for c in df.columns]
            first_col = str(df.columns[0]).lower()
            if 'eastern' in first_col or 'eastern conference' in cols:
                east_df = df
            elif 'western' in first_col or 'western conference' in cols:
                west_df = df

        # Se il detection automatico non trova i titoli, usiamo l'indice predefinito
        if east_df is None and len(dfs) >= 1:
            east_df = dfs[0]
        if west_df is None and len(dfs) >= 2:
            west_df = dfs[1]

        def process_conference_table(df):
            teams_list = []
            if df is None:
                return teams_list
            
            # Normalizza le colonne
            df.columns = [str(c).strip() for c in df.columns]
            team_col = df.columns[0] # La prima colonna contiene il nome squadra
            
            for _, row in df.iterrows():
                raw_name = str(row.get(team_col, '')).strip()
                if not raw_name or 'Conference' in raw_name or 'Division' in raw_name:
                    continue
                
                # Pulisci il nome della squadra (rimuovi eventuali asterisco o note playoff)
                clean_name = raw_name.replace('*', '').strip().upper()
                
                def safe_val(key, default='0'):
                    val = str(row.get(key, default)).strip()
                    return val if val != 'nan' else default

                def safe_pct(key):
                    val = str(row.get(key, '.000')).strip()
                    try:
                        f_val = float(val)
                        return f".{int(round(f_val * 1000)):03d}" if f_val < 1 else "1.000"
                    except:
                        return val

                team_obj = {
                    "Team": clean_name,
                    "W": safe_val('W', '0'),
                    "L": safe_val('L', '0'),
                    "WinPct": safe_pct('W/L%') if 'W/L%' in row else safe_pct('PCT'),
                    "GB": safe_val('GB', '—'),
                    "Home": safe_val('Home', '0-0'),
                    "Road": safe_val('Road', '0-0'),
                    "Last10": safe_val('L10', safe_val('Last 10', '0-0')),
                    "Streak": safe_val('Strk', safe_val('Streak', ''))
                }
                teams_list.append(team_obj)
            return teams_list

        eastern_data = process_conference_table(east_df)
        western_data = process_conference_table(west_df)

        final_output = {
            "eastern": eastern_data,
            "western": western_data
        }

        with open("nba-standings-data.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
        
        print("File nba-standings-data.json generato con successo!")

    except Exception as e:
        print(f"Errore durante il recupero delle standings: {e}")

if __name__ == "__main__":
    fetch_nba_standings()
