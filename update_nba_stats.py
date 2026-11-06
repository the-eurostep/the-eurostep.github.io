import urllib.request
import json

def test_nba_cdn():
    print("=== TEST DI VERIFICA DATI NBA (Stagione 2026-27) ===")
    
    # Intestazioni standard per simulare una richiesta pulita da browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com'
    }

    # Endpoint diretto stats.nba.com configurato per la stagione 2026-27
    url_players = "https://stats.nba.com/stats/leaguedashplayerstats?PerMode=PerGame&Season=2026-27&SeasonType=Regular%20Season"
    
    try:
        print(f"Tentativo di connessione a: {url_players}")
        req = urllib.request.Request(url_players, headers=headers)
        
        # Impostiamo un timeout di 30 secondi
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            print(f"Risposta ricevuta dal server! Codice HTTP: {status_code}")
            
            data = json.loads(response.read().decode('utf-8'))
            result_sets = data.get('resultSets', [])
            
            if result_sets:
                headers_list = result_sets[0].get('headers', [])
                rows = result_sets[0].get('rowSet', [])
                
                print(f"\n[ESITO POSITIVO] Trovati {len(rows)} giocatori nella stagione 2026-27!")
                print(f"Prime colonne disponibili: {headers_list[:10]}")
                
                # Stampiamo i dati del primo giocatore per controllo visivo
                if len(rows) > 0:
                    first_player = rows[0]
                    p_name_idx = headers_list.index('PLAYER_NAME') if 'PLAYER_NAME' in headers_list else 1
                    pts_idx = headers_list.index('PTS') if 'PTS' in headers_list else -1
                    team_idx = headers_list.index('TEAM_ABBREVIATION') if 'TEAM_ABBREVIATION' in headers_list else -1
                    
                    print(f"Esempio Giocatore #1: {first_player[p_name_idx]} ({first_player[team_idx]}) - {first_player[pts_idx]} PTS/game")
            else:
                print("[ATTENZIONE] Il server ha risposto ma la struttura resultSets è vuota.")
                
    except Exception as e:
        print(f"\n[ERRORE DI CONNECIONE] Impossibile raggiungere l'endpoint: {e}")

    # Creiamo un file temporaneo fittizio per evitare che il git push del workflow dia errore
    with open("nba-data.json", "w", encoding="utf-8") as f:
        json.dump({"test": "in_progress"}, f)

if __name__ == "__main__":
    test_nba_cdn()
