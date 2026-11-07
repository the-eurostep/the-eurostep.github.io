import json
import unicodedata
import pandas as pd
import requests

def clean_text(text):
    if not text or text == 'nan':
        return ''
    text = str(text)
    # Rimuove note come asterischi o spazi superflui
    text = text.replace('*', '').strip()
    # Normalizza i caratteri speciali per evitare problemi di encoding
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return text.upper()

def fetch_euroleague_standings():
    print("Scaricamento della classifica Eurolega da Basketball Reference...")
    url = "https://www.basketball-reference.com/international/euroleague/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Errore nella richiesta HTTP: status {response.status_code}")
            return

        dfs = pd.read_html(response.text)
        standings_df = None

        # Cerchiamo la tabella che ha esattamente le colonne W, L, W/L% come nell'immagine
        for df in dfs:
            # Se le colonne sono un MultiIndex (intestazioni su più righe), le appiattiamo
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(str(c) for c in col).strip() for col in df.columns]
            
            cols = [str(c).upper() for c in df.columns]
            if any('W' in c for c in cols) and any('L' in c for c in cols) and any('W/L%' in c or 'PCT' in c for c in cols):
                standings_df = df
                break

        # Fallimento di sicurezza: prendiamo la prima tabella disponibile se non trovata con i filtri
        if standings_df is None and len(dfs) > 0:
            standings_df = dfs[0]

        teams_list = []
        if standings_df is not None:
            standings_df.columns = [str(c).strip() for c in standings_df.columns]
            team_col = standings_df.columns[0] # La prima colonna è il nome della squadra

            for _, row in standings_df.iterrows():
                raw_name = str(row.get(team_col, '')).strip()
                # Filtra le righe di intestazione o vuote
                if not raw_name or 'Standings' in raw_name or 'Regular' in raw_name or 'Team' in raw_name or raw_name == 'nan':
                    continue

                clean_name = clean_text(raw_name)

                # Estrazione sicura di W e L basata sulle posizioni o sui nomi delle colonne
                def get_numeric_val(col_names):
                    for col in standings_df.columns:
                        if any(k == col.upper() for k in col_names):
                            try:
                                val = str(row.get(col, 0)).strip()
                                val_clean = ''.join(c for c in val if c.isdigit() or c == '.')
                                if val_clean:
                                    return int(float(val_clean))
                            except:
                                pass
                    return 0

                w = get_numeric_val(['W'])
                l = get_numeric_val(['L'])
                
                # Se W e L sono entrambi 0, proviamo a leggerli per indice (colonna 1 e colonna 2)
                if w == 0 and l == 0:
                    try:
                        w = int(float(str(row.iloc[1]).strip()))
                        l = int(float(str(row.iloc[2]).strip()))
                    except:
                        pass

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
        
        print("File euroleague-standings-data.json generato con successo e dati corretti!")

    except Exception as e:
        print(f"Errore durante il recupero delle standings Eurolega: {e}")

if __name__ == "__main__":
    fetch_euroleague_standings()
