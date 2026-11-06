import time
import json
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats

def test_nba_api_secure():
    print("=== AVVIO TEST SICURO NBA_API (Stagione 2026-27) ===")
    
    try:
        # Tentativo di scaricare le statistiche dei giocatori per la stagione 2026-27
        print("Richiesta statistiche giocatori in corso...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            per_mode_detailed='PerGame',
            season='2026-27',
            timeout=30
        )
        
        # Convertiamo la risposta in un dizionario Python
        p_dict = player_stats.get_dict()
        p_rows = p_dict['resultSets'][0]['rowSet']
        
        print(f"[SUCCESSO] Trovati {len(p_rows)} giocatori per la stagione 2026-27!")
        
        # Pausa di cortesia per non sovraccaricare il server
        time.sleep(2)
        
        # Tentativo di scaricare le statistiche delle squadre
        print("Richiesta statistiche squadre in corso...")
        team_stats = leaguedashteamstats.LeagueDashTeamStats(
            per_mode_detailed='PerGame',
            season='2026-27',
            timeout=30
        )
        
        t_dict = team_stats.get_dict()
        t_rows = t_dict['resultSets'][0]['rowSet']
        
        print(f"[SUCCESSO] Trovate {len(t_rows)} squadre per la stagione 2026-27!")

    except Exception as e:
        print(f"[ERRORE DURANTE IL TEST]: {e}")

    # Creiamo un file JSON temporaneo di riserva per non bloccare Git
    with open("nba-data.json", "w", encoding="utf-8") as f:
        json.dump({"players": [], "teams": []}, f)

if __name__ == "__main__":
    test_nba_api_secure()
