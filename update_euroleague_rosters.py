import json
import urllib.request

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Errore nel recupero di {url}: {e}")
        return None

def main():
    print("Sincronizzazione squadre Eurolega 2026...")
    clubs_url = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2026/clubs"
    clubs_data = fetch_json(clubs_url)
    
    if not clubs_data:
        print("Impossibile recuperare i club.")
        return

    teams_list = []
    all_rosters = {}

    # Estrazione dei club dal feed ufficiale
    clubs = clubs_data.get('clubs', [])
    for club in clubs:
        club_code = club.get('code')
        club_name = club.get('name')
        club_image = club.get('images', {}).get('crest', '') # Logo squadra

        teams_list.append({
            "code": club_code,
            "name": club_name,
            "image": club_image
        })

        print(f"Scaricamento roster per: {club_name} ({club_code})...")
        people_url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2026/clubs/{club_code}/people"
        people_data = fetch_json(people_url)
        
        roster_players = []
        if people_data and 'persons' in people_data:
            for person in people_data['persons']:
                person_code = person.get('code')
                
                # Fetch delle statistiche individuali del giocatore
                stats_url = f"https://api-live.euroleague.net/v2/competitions/E/seasons/E2026/people/{person_code}/stats"
                stats_data = fetch_json(stats_url)
                
                player_stats = {}
                if stats_data:
                    # Estraiamo le medie tradizionali se disponibili nel feed delle stats
                    player_stats = stats_data.get('averages', {})

                roster_players.append({
                    "code": person_code,
                    "name": person.get('name'),
                    "surname": person.get('surname'),
                    "number": person.get('dossard'),
                    "position": person.get('positionName'),
                    "height": person.get('height'),  # es. in cm
                    "weight": person.get('weight'),  # es. in kg
                    "nationality": person.get('nationality', {}).get('name'),
                    "birthDate": person.get('birthDate'),
                    "image": person.get('images', {}),
                    "stats": player_stats
                })

        all_rosters[club_code] = roster_players

    final_output = {
        "teams": teams_list,
        "rosters": all_rosters
    }

    with open('euroleague-rosters.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print("Aggiornamento completato con successo! Salvato in euroleague-rosters.json")

if __name__ == '__main__':
    main()
