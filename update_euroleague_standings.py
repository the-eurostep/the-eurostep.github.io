import json
import unicodedata
import pandas as pd
import requests

def clean_text(text):
    if not text or text == 'nan':
        return ''
    # Normalizza i caratteri speciali (es. gestisce accenti e codifiche strane)
    text = str(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Pulizie extra per caratteri sporchi residui
    text = text.replace('Ã', '').replace('Â', '').replace('½', '')
    return text.strip().upper()

def fetch_euroleague_standings():
    print("Scaricamento della classifica Eurolega da Basketball Reference...")
    url = "https://www.basketball-reference.com/international/euroleague/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # Forza la codifica corretta per i caratteri speciali
        
        if response.status_code != 200:
            print(f"Errore nella richiesta HTTP: status {response.status_code}")
            return

        dfs = pd.read_html(response.text)
        standings_df = None

        # Cerca la tabella che contiene le colonne W e L o record simili
        for df in dfs:
            cols = [str(c).upper() for c in df.columns]
            # Cerchiamo tabelle che contengano W/L o record di vittorie
            if any('W' in c for c in cols) and any('L' in c for c in cols):
                standings_df = df
                break

        if standings_df is None and len(dfs) > 0:
            standings_df = dfs[0]

        teams_list = []
        if standings_df is not None:
            # Pulisci i nomi delle colonne
            standings_df.columns = [str(c).strip() for c in standings_df.columns]
            team_col = standings_df.columns[0]

            for _, row in standings_df.iterrows():
                raw_name = str(row.get(team_col, '')).strip()
                if not raw_name or 'Standings' in raw_name or 'Team' in raw_name or 'Conference' in raw_name:
                    continue

                clean_name = clean_text(raw_name.replace('*', ''))

                def safe_int(keys):
                    if isinstance(keys, str):
                        keys = [keys]
                    for k in keys:
                        if k in standings_df.columns:
                            try:
                                val = str(row.get(k, 0)).strip()
                                # Rimuove eventuali caratteri non numerici
                                val_clean = ''.join(c for c in val if c.isdigit() or c == '.')
                                if val_clean:
                                    return int(float(val_clean))
                            except:
                                pass
                    return 0

                w = safe_int(['W', 'Wins', 'W_1'])
                l = safe_int(['L', 'Losses', 'L_1'])
                
                # Cerca GP o G, altrimenti calcola W + L
                gp = safe_int(['G', 'GP', 'Games'])
                if gp == 0:
                    gp = w + l

                win_pct = round(w / gp, 3) if gp > 0 else 0.0

                team_obj = {
                    "Team": clean_name,
                    "GP": gp,
                    "W": w,
                    "L": l,
                    "WinPct": f".{int(round(win_pct * 1000)):03d}" if win_pct < 1 else "1.000",
                    "raw_win_pct": win_pct
                }
                teams_list.append(team_obj)

            # Ordina le squadre per Vittorie (decrescente), poi per Sconfitte (crescente)
            teams_list.sort(key=lambda x: (x['W'], -x['L']), reverse=True)

        final_output = {
            "standings": teams_list
        }

        with open("euroleague-standings-data.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
        
        print("File euroleague-standings-data.json generato correttamente con caratteri puliti e dati numerici validi!")

    except Exception as e:
        print(f"Errore durante il recupero delle standings Eurolega: {e}")

if __name__ == "__main__":
    fetch_euroleague_standings()
