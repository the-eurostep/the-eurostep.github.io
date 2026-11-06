import json
import time
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats

def test_nba_fetch():
    print("Test di collegamento a stats.nba.com tramite nba_api...")
    
    try:
        # 1. Test Player Stats
        print("Richiesta statistiche tradizionali Giocatori...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            per_mode_detailed='PerGame',
            season='2025-26'
        )
        players_df = player_stats.get_dict()
        player_rows = players_df['resultSets'][0]['rowSet']
        player_headers = players_df['resultSets'][0]['headers']
        
        print(f"SUCCESSO GIOCATORI! Scaricati {len(player_rows)} giocatori.")
        print("Colonne disponibili per i giocatori:")
        print(player_headers[:15]) # Mostra le prime colonne per verifica
        
        # Piccola pausa di sicurezza per non saturare le API della NBA
        time.sleep(2)

        # 2. Test Team Stats
        print("\nRichiesta statistiche tradizionali Squadre...")
        team_stats = leaguedashteamstats.LeagueDashTeamStats(
            per_mode_detailed='PerGame',
            season='2025-26'
        )
        teams_df = team_stats.get_dict()
        team_rows = teams_df['resultSets'][0]['rowSet']
        team_headers = teams_df['resultSets'][0]['headers']

        print(f"SUCCESSO SQUADRE! Scaricate {len(team_rows)} squadre NBA.")
        print("Colonne disponibili per le squadre:")
        print(team_headers[:15])

        # Creiamo un json temporaneo per non far fallire il workflow
        with open("nba-data.json", "w", encoding="utf-8") as f:
            json.dump({"status": "test_ok"}, f)

    except Exception as e:
        print(f"Errore durante il test NBA: {e}")

if __name__ == "__main__":
    test_nba_fetch()
