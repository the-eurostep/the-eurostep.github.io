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
    
    if not clubs_data or 'data' not in clubs_data:
        print("Impossibile recuperare i club o struttura non valida.")
        return

    teams_list = []
    all_rosters = {}

    clubs = clubs_data.get('data', [])
    for club in clubs:
        club_code = club.get('code')
        club_name = club.get('name')
        club_image = club.get('images', {}).get('crest', '')

        print(f"Scaricamento roster per: {club_name} ({club_code})...")
        people_url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2026/clubs/{club_code}/people"
        people_data = fetch_json(people_url)
        
        roster_players = []
        coaches_list = []

        if isinstance(people_data, list):
            for entry in people_data:
                type_name = entry.get('typeName')
                person = entry.get('person', {})
                images = entry.get('images', {})
                
                # Nome e cognome puliti
                full_name = person.get('name', '')
                parts = full_name.split(',')
                if len(parts) == 2:
                    surname = parts[0].strip()
                    name = parts[1].strip()
                else:
                    name = full_name
                    surname = ""

                # Raccolta Coach per selezione intelligente
                if type_name == "Coach":
                    coaches_list.append({
                        "name": f"{name} {surname}".strip(),
                        "active": entry.get('active', False),
                        "startDate": entry.get('startDate', '')
                    })

                # Estrazione Giocatori (Filtro rigoroso)
                elif type_name == "Player":
                    country_obj = person.get('country')
                    nat_name = country_obj.get('name') if isinstance(country_obj, dict) else 'N/A'

                    roster_players.append({
                        "code": person.get('code'),
                        "name": name,
                        "surname": surname,
                        "number": entry.get('dorsal'),
                        "position": entry.get('positionName'),
                        "height": person.get('height'),
                        "weight": person.get('weight'),
                        "nationality": nat_name,
                        "birthDate": person.get('birthDate'),
                        "image": images.get('headshot') or images.get('action', '')
                    })

        # Selezione Head Coach: priorità agli attivi, ordinati per data d'inizio più recente
        head_coach_name = "N/A"
        if coaches_list:
            # Filtra prima i coach attivi (active == True)
            active_coaches = [c for c in coaches_list if c['active']]
            target_list = active_coaches if active_coaches else coaches_list
            
            # Ordina per startDate decrescente (la più recente per prima)
            target_list.sort(key=lambda x: x['startDate'], reverse=True)
            head_coach_name = target_list[0]['name']

        teams_list.append({
            "code": club_code,
            "name": club_name,
            "image": club_image,
            "headCoach": head_coach_name
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
