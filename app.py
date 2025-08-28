import streamlit as st
from datetime import datetime, date
import pandas as pd 
from bs4 import BeautifulSoup
from random import choice 
import requests 

def subtract_years(d, years):
    """Return a date `years` earlier than d, handling Feb 29 safely."""
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        # Handle Feb 29 -> Feb 28 on non-leap years
        return d.replace(month=2, day=28, year=d.year - years)


st.set_page_config(page_title="GBE ESC Checker", page_icon="👋", layout="centered", initial_sidebar_state="expanded")


def getNationalTeam(playerURL, transferDate):
    
    def get_souped_page(page_url):
        headers_list = [
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        ]
        headers = choice(headers_list)
        pageTree = requests.get(page_url, headers=headers)
        pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
        return(pageSoup)


    nationalTeamURL = playerURL.replace('profil', 'nationalmannschaft')
    soup = get_souped_page(nationalTeamURL)


#             d['table2'] = [option['value'] for option in table2]

    teamOptions = [{'teamID': str(option['value']), 'teamName': option.text.strip()} for option in soup.find_all('table')[0].find_all('option')]

    allMatches = []
    for team in teamOptions:
        
        part1 =  '/verein_id/' + team['teamID'] + '/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=' 
        startDate_date = subtract_years(transferDate, 2)
        startDate = startDate_date.strftime("%d.%m.%Y")
        part2 = '&ende=' + transferDate.strftime("%d.%m.%Y") + '&nurEinsatz=0'
        nationalTeamURLSubSection =  nationalTeamURL + part1 + startDate + part2
        soup2 = get_souped_page(nationalTeamURLSubSection)
        
        print(nationalTeamURLSubSection)
        
        if len(soup2.find_all('table')) >= 3:
            table = soup2.find_all('table')[3]
            tbody = table.find('tbody')

            matches = []
            for row in tbody.find_all('tr'):
                if len(row.find_all('td')) == 2:
                    if len(matches) > 0:
                        allMatches += matches
                    competition = row.find_all('td')[0].find('img')['title']
                    competitionID = row.find_all('td')[0].find('a')['name']
                    matches = []
                else: 
                    cells = row.find_all('td')
                    d = {
                            'competition': competition,
                            'competitionID': competitionID,
                            'a' : cells[2].text,
                            'home/away': cells[3].text,
                            'for': cells[4].find('a')['title'],
                            'against': cells[6].text.strip(),
                            'result':cells[7].text.strip(),
                        }
                    
                    
                    if 'Not in squad' not in row.text:
                        d['minutesPlayed'] = int(cells[14].text.replace("'", ""))

                        if d['minutesPlayed'] > 0:
                            d['played'] = True
                        else:
                            d['played'] = False

                        d['teamID'] = team['teamID']
                        d['teamName'] = team['teamName']
                        matches.append(d)
                    elif 'Not in squad' in row.text:
                        d['played'] = False
                        d['minutesPlayed'] = 0
                        d['teamID'] = team['teamID']
                        d['teamName'] = team['teamName']
                        matches.append(d)
            
            allMatches += matches
            

    ntInfo = allMatches
    # ntInfo = teamOptions

    return ntInfo
            

# ------- undected scrap for Transfermarkt -------- #
def get_souped_page(page_url):
        headers_list = [
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        ]
        headers = choice(headers_list)
        pageTree = requests.get(page_url, headers=headers)
        pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
        return(pageSoup)



def parsePlayer(url):

    store = {}

    # ------- get soups -------- #

    soup = get_souped_page(url)

    nationalTeamURL = url.replace('profil', 'nationalmannschaft')
    soupNationalTeam = get_souped_page(nationalTeamURL)
    # https://www.transfermarkt.co.uk/jude-bellingham/nationalmannschaft/spieler/581678/verein_id/3299/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2025&ende=27.08.2025&nurEinsatz=0 

    # ------- name -------- #
    store['name'] = soup.find('h1').text.split('\n')[3].strip()
    
    # ------- info -------- #
    infoRaw = soup.find_all('li', class_ = 'data-header__label')
    
    for li in infoRaw: 
        if 'Date of birth/Age:' in li.text:
            items = li.text.split(':')[1].split('(')[0].strip().split('.')
            store['dayBirth'] = int(items[0])
            store['monthBirth'] = int(items[1])
            store['yearBirth'] = int(items[2])

        if 'Place of birth:' in li.text:
            store['placeBirth'] = li.text.split(':')[1].strip()
            store['countryBirth'] = li.find('img')['title']
            
        if 'Citizenship' in li.text:   
            if len(li.find_all('img')) == 1:                     
                store['citizensip1'] = li.find_all('img')[0]['title']
                store['citizensip2'] = None
            elif len(li.find_all('img')) == 2:                     
                store['citizensip2'] = li.find_all('img')[1]['title']
            else:
                store['citizensip1'] = None
                store['citizensip2'] = None

        if 'Height' in li.text:  
            store['height'] = int(li.text.split(':')[1].strip().replace(',','').replace('m', '').strip())

    
        if 'Position' in li.text: 
            store['position'] = li.text.split(':')[1].strip() 

        if 'Current international:' in li.text: 
            store['nationalTeam'] = li.find('img')['title']

        if 'Caps/Goals' in li.text:
            parts =  li.text.split(':')[1].strip().split('/')
            store['internationalCaps'] = int(parts[0])
            store['internationalGoals'] = int(parts[1])


    # ------- big box -------
    bigBox = soup.find('div', class_= 'data-header__box--big')
    
    store['currentClub'] = bigBox.find('img')['alt']
    store['currentClubURL'] = bigBox.find('a')['href']
    store['currentClubID'] = int(store['currentClubURL'].split('/')[-1])
    
    leagueInfo = bigBox.find('span', class_='data-header__league')

    store['currentLeague'] = leagueInfo.find('img')['alt']
    store['currentLeagueURL'] = leagueInfo.find('a')['href']
    store['currentLeagueID'] = store['currentLeagueURL'].split('/')[-1]
    
    store['clubImage'] = leagueInfo.find('img')['src']

    labels = bigBox.find_all('span', class_= 'data-header__label')

    for label in labels: 

        if 'League level:' in label.text:
            leagueTierText = label.text.split(':')[1].strip()
            if leagueTierText == 'First Tier':
                store['leagueTier'] = 1
            elif leagueTierText == 'Second Tier':
                store['leagueTier'] = 2    
            elif leagueTierText == 'Second Tier':
                store['leagueTier'] = 2 
            elif leagueTierText == 'Third Tier':
                store['leagueTier'] = 3 
            elif leagueTierText == 'Fourth Tier':
                store['leagueTier'] = 4 
            elif leagueTierText == 'Fifth Tier':
                store['leagueTier'] = 5           

        if 'Contract expires:' in label.text:
            items = label.text.split(':')[1].split('(')[0].strip().split('.')
            store['dayContractExpires'] = int(items[0])
            store['monthContractExpires'] = int(items[1])
            store['yearContractExpires'] = int(items[2])
            contract_date = datetime(store['yearContractExpires'], store['monthContractExpires'], store['dayContractExpires'])
            today = datetime.today()
            delta = contract_date - today
            store['daysUntilContractExpires'] = delta.days
            store['monthsUntilContractExpires'] = (contract_date.year - today.year) * 12 + (contract_date.month - today.month)

        if 'League level' in label.text:
            store['currentLeagueCountry'] = label.find('img')['title']


    # store['labels'] = labels



    return store

# def _on_player_url_change():
#     url = st.session_state.get('playerURL', '')
#     if url:
#         st.session_state['playerInfo'] = parsePlayer(url)


APP_PASSWORD = "letmein"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.sidebar:
        st.header("Login")
        password = st.text_input("Enter password", type="password")
        if st.button("Force rerun", key="force_rerun_login"):
            st.rerun()
    if password:
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
        else:
            st.error("Wrong password, try again.")

if st.session_state.authenticated:
    with st.sidebar:
        if st.button("Force rerun", key="force_rerun_authed"):
            st.rerun()
    st.title('GBE/ESC Checker')

    playerURL = st.text_input('playerURL', value="")
    playerInfo = None
    if playerURL != "":
        playerInfo = parsePlayer(playerURL)
        # st.write(playerURL)
        # st.write(playerInfo)

        



    if playerInfo != None:
        # TODO add the min value for production
        transferDate  = st.date_input("When is the proposed transfer?", date.today())
        # transferDate  = st.date_input("When is the proposed transfer?", date.today(),     min_value=date.today())

        # --- Age check callout (18+) ---
        try:
            dob = date(playerInfo['yearBirth'], playerInfo['monthBirth'], playerInfo['dayBirth'])
            
            # Compute age at transferDate
            age_years = transferDate.year - dob.year - ((transferDate.month, transferDate.day) < (dob.month, dob.day))

            if age_years >= 18:
                st.success(f"Player will be {age_years} on {transferDate.strftime('%d %b %Y')} — meets 18+ requirement.")
            else:
                st.error(f"Player will be {age_years} on {transferDate.strftime('%d %b %Y')} — under 18.")
        except Exception as e:
            st.warning(f"Could not determine age: {e}")

        # --- Player overview ---
        with st.container():
            st.markdown("### " + playerInfo.get('name', ''))
            # Compute DOB string and age safely (relative to transferDate)
            try:
                dob = date(playerInfo['yearBirth'], playerInfo['monthBirth'], playerInfo['dayBirth'])
                age_years = transferDate.year - dob.year - ((transferDate.month, transferDate.day) < (dob.month, dob.day))
                dob_str = dob.strftime('%d %b %Y')
            except Exception:
                age_years = None
                dob_str = "Unknown"

            colA, colB, colC, colD = st.columns([1, 2, 2, 2])
            with colA:
                crest = playerInfo.get('clubImage')
                if crest:
                    st.image(crest, use_container_width=False)
            with colB:
                country = playerInfo.get('citizensip1') or playerInfo.get('countryBirth', '')
                st.markdown(f"**Country:** {country}")
                st.markdown(f"**DOB / Age:** {dob_str} / {age_years if age_years is not None else '—'}")
            with colC:
                st.markdown(f"**Club:** {playerInfo.get('currentClub', '')}")
                st.markdown(f"**League:** {playerInfo.get('currentLeague', '')}")
            with colD:
                st.markdown(f"**League country:** {playerInfo.get('currentLeagueCountry', '')}")
                st.markdown(f"**Position:** {playerInfo.get('position', '')}")

        ntInfo = pd.DataFrame(getNationalTeam(playerURL, transferDate))

        # Show per-team metrics and table
        for team in sorted(ntInfo['for'].unique()):
            team_df = ntInfo[ntInfo['for'] == team].copy()
            team_games = len(team_df)
            player_games = int(team_df['played'].sum()) if 'played' in team_df.columns else 0
            pct_played = (player_games / team_games * 100) if team_games else 0.0

            st.subheader(team)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Team matches", team_games)
            with col2:
                st.metric("Player played", player_games)
            with col3:
                st.metric("% of team matches", f"{pct_played:.1f}%")

            # st.table(team_df)

  
        
        # transferDate
        # day month year 
        # soupNationalTeam = get_souped_page(nationalTeamURL)
    # https://www.transfermarkt.co.uk/jude-bellingham/nationalmannschaft/spieler/581678/verein_id/3299/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2025&ende=27.08.2025&nurEinsatz=0 

# https://www.transfermarkt.co.uk/luka-hyrylainen/nationalmannschaft/spieler/716898/verein_id/20796/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2024&ende=28.08.2025&nurEinsatz=0
# https://www.transfermarkt.co.uk/luka-hyrylainen/nationalmannschaft/spieler/716898/verein_id/3299/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2024&ende=27.08.2025&nurEinsatz=0
if __name__ == "__main__":
    pass