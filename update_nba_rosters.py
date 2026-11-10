import json
import urllib.request
from datetime import datetime

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Errore nel recupero di {url}: {e}")
        return None

def main():
    print("Avvio sincronizzazione NBA...")

    # 1. Recupero Squadre e Loghi Ufficiali da Yahoo Sports (Fonte Primaria Squadre)
    yahoo_url = "https://graphite.sports.yahoo.com/v1/query/shangrila/navDropdownTray?lang=en-US&region=US&ysp_platform=next-app-sports"
    yahoo_data = fetch_json(yahoo_url)
    
    yahoo_teams = []
    if yahoo_data and 'nba' in yahoo_data:
        for section in yahoo_data['nba']:
            if 'teams' in section:
                for t in section['teams']:
                    display_name = t.get('displayName', '').strip() # es. "Atlanta"
                    alias_url = t.get('alias', {}).get('url', '') # es. "https://sports.yahoo.com/nba/teams/atlanta/"
                    logo_url = t.get('teamLogo', {}).get('url', '')
                    
                    # Estraiamo lo slug dall'alias URL (es. "atlanta")
                    slug = alias_url.strip('/').split('/')[-1].lower() if alias_url else display_name.lower()
                    
                    if display_name and logo_url:
                        yahoo_teams.append({
                            "slug": slug,
                            "displayName": display_name,
                            "logo": logo_url
                        })

    # 2. Recupero Elenco Competitor da TSN (per mappare i roster)
    tsn_teams_url = "https://next-gen.sports.bellmedia.ca/v2/competitor/basketball/nba/"
    tsn_teams = fetch_json(tsn_teams_url)

    if not tsn_teams or not isinstance(tsn_teams, list):
        print("Impossibile recuperare l'elenco squadre da TSN.")
        return

    # Mappiamo i dati di TSN per nome/location normalizzati
    tsn_map = {}
    for tsn_t in tsn_teams:
        comp_id = tsn_t.get('competitorId')
        name = tsn_t.get('name', '').strip() # es. "Atlanta Hawks"
        location = tsn_t.get('location', '').strip().lower() # es. "atlanta"
        if comp_id and name:
            tsn_map[location] = {
                "competitorId": comp_id,
                "fullName": name
            }

    teams_list = []
    all_rosters = {}
    current_year = datetime.now().year

    # 3. Unione pulita basata sui dati Yahoo arricchiti con i roster TSN
    for y_team in yahoo_teams:
        slug = y_team['slug']
        logo = y_team['logo']
        
        # Cerchiamo la corrispondenza in TSN usando lo slug/location di Yahoo
        matched_tsn = tsn_map.get(slug)
        
        # Fallback di ricerca parziale se lo slug Yahoo è contenuto nel nome TSN o viceversa
        if not matched_tsn:
            for tsn_loc, tsn_data in tsn_map.items():
                if slug in tsn_loc or tsn_loc in slug:
                    matched_tsn = tsn_data
                    break
        
        if not matched_tsn:
            continue

        competitor_id = matched_tsn['competitorId']
        full_name = matched_tsn['fullName']
        team_code = str(competitor_id)

        # Recupero Roster per la squadra attuale da TSN
        roster_url = f"https://next-gen.sports.bellmedia.ca/v2/competitor/basketball/nba/{competitor_id}/roster?brand=tsn&lang=en"
        roster_data = fetch_json(roster_url)

        roster_players = []
        if roster_data and isinstance(roster_data, list):
            for p in roster_data:
                player_id = p.get('playerId')
                first_name = p.get('firstName', '').strip()
                last_name = p.get('lastName', '').strip()
                
                # Gestione rigorosa del numero di maglia (inclusi 0 e 00)
                num_val = p.get('number')
                if num_val is not None and num_val != "":
                    number = str(num_val)
                else:
                    number = "-"

                position = p.get('positionShort', 'N/A')
                
                feet = p.get('heightFeet', 0)
                inches = p.get('heightInches', 0)
                height_str = f"{feet}' {inches}\"" if feet else "N/A"
                
                weight_val = p.get('weight')
                weight_str = f"{weight_val} lbs" if weight_val else "N/A"
                
                birth_date = p.get('birthDate', '')
                if birth_date:
                    try:
                        birth_date_str = birth_date.split('T')[0]
                    except:
                        birth_date_str = birth_date
                else:
                    birth_date_str = "N/A"

                birth_place = p.get('birthPlace', '').strip()
                birth_place_str = birth_place if birth_place else "N/A"
                
                draft_year = p.get('draftYear')
                if draft_year and isinstance(draft_year, int):
                    exp_years = current_year - draft_year
                    experience = f"{exp_years} yr" if exp_years == 1 else f"{exp_years} yrs"
                    if exp_years <= 0:
                        experience = "Rookie"
                else:
                    experience = "Rookie"

                roster_players.append({
                    "id": player_id,
                    "name": first_name,
                    "surname": last_name,
                    "number": number,
                    "position": position,
                    "height": height_str,
                    "weight": weight_str,
                    "birthDate": birth_date_str,
                    "birthPlace": birth_place_str,
                    "experience": experience
                })

        teams_list.append({
            "code": team_code,
            "name": full_name,
            "image": logo
        })

        all_rosters[team_code] = roster_players

    # 4. Ordinamento Alfabetico (A-Z) delle squadre
    teams_list.sort(key=lambda x: x['name'])

    final_output = {
        "teams": teams_list,
        "rosters": all_rosters
    }

    with open('nba-rosters.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"Completato! Elaborate {len(teams_list)} squadre e generato nba-rosters.json con i loghi Yahoo.")

if __name__ == '__main__':
    main()
