import json
import pandas as pd
import requests

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

        dfs = pd.read_html(response.text)
        east_df = None
        west_df = None

        for df in dfs:
            cols = [str(c).lower() for c in df.columns]
            first_col = str(df.columns[0]).lower()
            if 'eastern' in first_col or 'eastern conference' in cols:
                east_df = df
            elif 'western' in first_col or 'western conference' in cols:
                west_df = df

        if east_df is None and len(dfs) >= 1:
            east_df = dfs[0]
        if west_df is None and len(dfs) >= 2:
            west_df = dfs[1]

        import re

        def process_conference_table(df):
            teams_list = []
            if df is None:
                return teams_list
            
            df.columns = [str(c).strip() for c in df.columns]
            team_col = df.columns[0]
            
            for _, row in df.iterrows():
                raw_name = str(row.get(team_col, '')).strip()
                if not raw_name or 'Conference' in raw_name or 'Division' in raw_name:
                    continue
                
                # Rimuove asterischi e numeri tra parentesi (es. "(1)" o simili)
                clean_name = re.sub(r'\s*\(\d+\)', '', raw_name)
                clean_name = clean_name.replace('*', '').strip().upper()
                
                def safe_int(key):
                    try:
                        val = str(row.get(key, 0)).strip()
                        return int(float(val))
                    except:
                        return 0

                w = safe_int('W')
                l = safe_int('L')
                gp = w + l
                win_pct = round(w / gp, 3) if gp > 0 else 0.0
                
                team_obj = {
                    "Team": clean_name,
                    "W": w,
                    "L": l,
                    "WinPct": f".{int(round(win_pct * 1000)):03d}" if win_pct < 1 else "1.000",
                    "raw_win_pct": win_pct,
                    "Home": str(row.get('Home', '0-0')),
                    "Road": str(row.get('Road', '0-0')),
                    "Last10": str(row.get('L10', row.get('Last 10', '0-0'))),
                    "Streak": str(row.get('Strk', row.get('Streak', '')))
                }
                teams_list.append(team_obj)

            # Ordina prima per Vittorie descrescente, poi per Sconfitte crescente
            teams_list.sort(key=lambda x: (x['W'], -x['L']), reverse=True)

            # Calcolo matematico rigoroso del GB (Games Behind) basato sulla prima in classifica
            if len(teams_list) > 0:
                top_w = teams_list[0]['W']
                top_l = teams_list[0]['L']
                for t in teams_list:
                    w = t['W']
                    l = t['L']
                    gb = ((top_w - w) + (l - top_l)) / 2.0
                    if gb == 0.0:
                        t['GB'] = "—"
                        t['raw_gb'] = 0.0
                    else:
                        t['GB'] = str(int(gb)) if gb.is_integer() else str(gb)
                        t['raw_gb'] = gb

            return teams_list

        eastern_data = process_conference_table(east_df)
        western_data = process_conference_table(west_df)

        final_output = {
            "eastern": eastern_data,
            "western": western_data
        }

        with open("nba-standings-data.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
        
        print("File nba-standings-data.json generato e corretto con successo!")

    except Exception as e:
        print(f"Errore durante il recupero delle standings: {e}")

if __name__ == "__main__":
    fetch_nba_standings()
