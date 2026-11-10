import json
import urllib.request
from datetime import datetime

TEAM_FULL_NAMES = {
    "Atlanta": "Atlanta Hawks",
    "Boston": "Boston Celtics",
    "Brooklyn": "Brooklyn Nets",
    "Charlotte": "Charlotte Hornets",
    "Chicago": "Chicago Bulls",
    "Cleveland": "Cleveland Cavaliers",
    "Dallas": "Dallas Mavericks",
    "Denver": "Denver Nuggets",
    "Detroit": "Detroit Pistons",
    "Golden State": "Golden State Warriors",
    "Houston": "Houston Rockets",
    "Indiana": "Indiana Pacers",
    "Los Angeles Clippers": "LA Clippers",
    "Los Angeles Lakers": "Los Angeles Lakers",
    "Memphis": "Memphis Grizzlies",
    "Miami": "Miami Heat",
    "Milwaukee": "Milwaukee Bucks",
    "Minnesota": "Minnesota Timberwolves",
    "New Orleans": "New Orleans Pelicans",
    "New York": "New York Knicks",
    "Oklahoma City": "Oklahoma City Thunder",
    "Orlando": "Orlando Magic",
    "Philadelphia": "Philadelphia 76ers",
    "Phoenix": "Phoenix Suns",
    "Portland": "Portland Trail Blazers",
    "Sacramento": "Sacramento Kings",
    "San Antonio": "San Antonio Spurs",
    "Toronto": "Toronto Raptors",
    "Utah": "Utah Jazz",
    "Washington": "Washington Wizards"
}

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
    print("Sincronizzazione squadre e roster NBA...")
    
    # 1. Recupero delle squadre da Yahoo Sports
    yahoo_url = "https://graphite.sports.yahoo.com/v1/query/shangrila/navDropdownTray?lang=en-US&region=US&ysp_platform=next-app-sports"
    data = fetch_json(yahoo_url)
    
    if not data:
        print("Impossibile contattare Yahoo Sports.")
        return

    nba_sections = data.get('nba', [])
    raw_teams = []
    for section in nba_sections:
        if 'teams' in section:
            raw_teams.extend(section['teams'])

    teams_list = []
    all_rosters = {}
    current_year = datetime.now().year

    # Ordinamento preliminare per assegnare un ID progressivo stabile da 1 a 30 basato sull'ordine alfabetico del nome completo
    sorted_raw_teams = sorted(
        raw_teams, 
        key=lambda t: TEAM_FULL_NAMES.get(t.get('displayName', ''), t.get('displayName', ''))
    )

    for index, team in enumerate(sorted_raw_teams, start=1):
        short_name = team.get('displayName', '')
        full_name = TEAM_FULL_NAMES.get(short_name, f"{short_name} Team")
        team_logo = team.get('teamLogo', {}).get('url', '')
        
        # Usiamo l'indice progressivo (1-30) che corrisponde alle 30 franchigie NBA ordinate alfabeticamente su TSN
        team_code = str(index)

        print(f"Elaborazione franchigia ({team_code}/30): {full_name}...")

        roster_players = []
        tsn_url = f"https://next-gen.sports.bellmedia.ca/v2/competitor/basketball/nba/{index}/roster?brand=tsn&lang=en"
        tsn_data = fetch_json(tsn_url)

        if isinstance(tsn_data, list):
            for p in tsn_data:
                player_id = p.get('playerId')
                first_name = p.get('firstName', '')
                last_name = p.get('lastName', '')
                number = p.get('number', '')
                position = p.get('positionShort', 'N/A')
                
                feet = p.get('heightFeet', 0)
                inches = p.get('heightInches', 0)
                height_str = f"{feet}' {inches}\"" if feet else "N/A"
                weight = p.get('weight', 'N/A')
                birth_date = p.get('birthDate', 'N/A')
                birth_place = p.get('birthPlace', 'N/A')
                
                draft_year = p.get('draftYear')
                if draft_year and isinstance(draft_year, int):
                    exp_years = current_year - draft_year
                    experience = f"{exp_years} yr" if exp_years == 1 else f"{exp_years} yrs"
                    if exp_years <= 0:
                        experience = "Rookie"
                else:
                    experience = "Rookie"

                headshot_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png" if player_id else ""

                roster_players.append({
                    "id": player_id,
                    "name": first_name,
                    "surname": last_name,
                    "number": number,
                    "position": position,
                    "height": height_str,
                    "weight": f"{weight} lbs" if weight != 'N/A' and weight else 'N/A',
                    "birthDate": birth_date,
                    "birthPlace": birth_place if birth_place else 'N/A',
                    "experience": experience,
                    "image": headshot_url
                })

        teams_list.append({
            "code": team_code,
            "name": full_name,
            "image": team_logo,
            "headCoach": "Staff Tecnico"
        })

        all_rosters[team_code] = roster_players

    # Ordinamento finale rigoroso A-Z sul nome completo
    teams_list.sort(key=lambda x: x['name'])

    final_output = {
        "teams": teams_list,
        "rosters": all_rosters
    }

    with open('nba-rosters.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print("File nba-rosters.json generato e popolato con successo!")

if __name__ == '__main__':
    main()
