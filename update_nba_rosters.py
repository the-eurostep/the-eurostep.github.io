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

    # 1. Recupero Squadre e Loghi DIRETTAMENTE da Yahoo Sports
    yahoo_url = "https://graphite.sports.yahoo.com/v1/query/shangrila/navDropdownTray?lang=en-US&region=US&ysp_platform=next-app-sports"
    yahoo_data = fetch_json(yahoo_url)
    
    yahoo_teams_dict = {}
    
    try:
        root_data = yahoo_data.get('data', yahoo_data)
        sections_to_check = []
        if isinstance(root_data, dict):
            for k, v in root_data.items():
                if isinstance(v, list):
                    sections_to_check.extend(v)
                elif isinstance(v, dict):
                    sections_to_check.append(v)
        elif isinstance(root_data, list):
            sections_to_check = root_data

        for item in sections_to_check:
            if isinstance(item, dict):
                if item.get('shortName') == 'NBA' or 'nba' in str(item.get('teamId', '')).lower():
                    teams_array = item.get('teams', [])
                    for t in teams_array:
                        display_name = t.get('displayName', '').strip().lower() # es. "la clippers", "la lakers", "atlanta"
                        logo_url = t.get('teamLogo', {}).get('url', '')
                        
                        if display_name and logo_url:
                            yahoo_teams_dict[display_name] = logo_url
    except Exception as e:
        print(f"Errore durante il parsing dei loghi Yahoo: {e}")

    # 2. Recupero Elenco Competitor da TSN (per i roster dei giocatori)
    tsn_teams_url = "https://next-gen.sports.bellmedia.ca/v2/competitor/basketball/nba/"
    tsn_teams = fetch_json(tsn_teams_url)

    if not tsn_teams or not isinstance(tsn_teams, list):
        print("Impossibile recuperare l'elenco squadre da TSN.")
        return

    teams_list = []
    all_rosters = {}
    current_year = datetime.now().year

    for team_info in tsn_teams:
        competitor_id = team_info.get('competitorId')
        full_name = team_info.get('name', '').strip() # es. "Los Angeles Lakers"
        location = team_info.get('location', '').strip() # es. "Los Angeles"
        nickname = team_info.get('nickname', '').strip() # es. "Lakers"
        
        if not competitor_id or not full_name:
            continue

        team_code = str(competitor_id)

        # Cerchiamo il logo corrispondente gestendo specificamente Los Angeles e le altre squadre
        logo = ""
        loc_lower = location.lower()
        full_lower = full_name.lower()
        nick_lower = nickname.lower()

        # Costruiamo le varianti di ricerca per Yahoo
        # Se la location è "Los Angeles", Yahoo la mappa come "la lakers" o "la clippers"
        potential_keys = [
            f"{loc_lower} {nick_lower}", # es. "los angeles lakers" (se Yahoo lo usasse)
            f"la {nick_lower}",         # es. "la lakers", "la clippers"
            loc_lower,                  # es. "atlanta"
            nick_lower                  # es. "lakers"
        ]

        for key in potential_keys:
            if key in yahoo_teams_dict:
                logo = yahoo_teams_dict[key]
                break
        
        # Ricerca di riserva parziale se nessuna chiave diretta ha funzionato
        if not logo:
            for y_key, y_logo in yahoo_teams_dict.items():
                if y_key in full_lower or full_lower in y_key or (nick_lower and nick_lower in y_key):
                    logo = y_logo
                    break

        # Recupero Roster Giocatori da TSN
        roster_url = f"https://next-gen.sports.bellmedia.ca/v2/competitor/basketball/nba/{competitor_id}/roster?brand=tsn&lang=en"
        roster_data = fetch_json(roster_url)

        roster_players = []
        if roster_data and isinstance(roster_data, list):
            for p in roster_data:
                player_id = p.get('playerId')
                first_name = p.get('firstName', '').strip()
                last_name = p.get('lastName', '').strip()
                
                num_val = p.get('number')
                number = str(num_val) if num_val is not None and num_val != "" else "-"

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

    teams_list.sort(key=lambda x: x['name'])

    final_output = {
        "teams": teams_list,
        "rosters": all_rosters
    }

    with open('nba-rosters.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"Completato! Elaborate {len(teams_list)} squadre con loghi Yahoo e generato nba-rosters.json.")

if __name__ == '__main__':
    main()
