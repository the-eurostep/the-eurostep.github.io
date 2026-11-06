import json
import urllib.request

def test_team_endpoint():
    # Questo è l'indirizzo ufficiale dedicato alle squadre
    url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/teams/traditional?seasonMode=Single&limit=100&sortDirection=descending&seasonCode=E2026&statisticMode=perGame&statisticSortMode=perGame"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }

    print("Sto provando a contattare l'archivio ufficiale delle squadre dell'Eurolega...")

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            
            print(">>> COLLEGAMENTO RIUSCITO CON SUCCESSO! <<<")
            print("Ecco un'anteprima dei dati grezzi che ci ha mandato l'Eurolega per le squadre:")
            
            # Stampiamo i primi 1500 caratteri della risposta per leggerla nei log
            print(json.dumps(data, indent=2)[:1500])
            
    except Exception as e:
        print(f"C'è stato un errore nel collegamento: {e}")

if __name__ == "__main__":
    test_team_endpoint()
