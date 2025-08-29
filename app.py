import streamlit as st
from datetime import datetime, date
import pandas as pd 
from bs4 import BeautifulSoup
from random import choice 
import requests 

from fifaPull import fetch_fifa_rankings_timeseries, average_rank

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
                    
                    
                    # Treat not in squad, injuries, or bench listings as not played
                    text_lower = row.text.lower()
                    print(text_lower)
                    not_in_squad = 'not in squad' in text_lower
                    injury = ('injury' in text_lower) or ('injured' in text_lower)
                    bench = ('bench' in text_lower) or ('on the bench' in text_lower)
                    national = 'national team' in text_lower
                    noInfo = 'no information' in text_lower
                    muscularProblems = 'muscular problems' in text_lower
                    ligamentInjury = 'ligament injury' in text_lower
                    adductorPain = 'adductor pain' in text_lower


                    if not (not_in_squad or injury or bench or 
                            national or noInfo or muscularProblems or 
                            ligamentInjury or adductorPain):
                        d['minutesPlayed'] = int(cells[14].text.replace("'", ""))

                        if d['minutesPlayed'] > 0:
                            d['played'] = True
                        else:
                            d['played'] = False

                        d['teamID'] = team['teamID']
                        d['teamName'] = team['teamName']
                        matches.append(d)
                    else:
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
    store['name'] = url.split('.co.uk/')[1].split('/')[0].replace('-', ' ').title()


    # https://www.transfermarkt.co.uk/lionel-messi/profil/spieler/28003
    
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
    
    store['clubImage'] = bigBox.find('img')['srcset']

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
            if '-' not in label.text.split(':')[1]:
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

    with st.expander("Settings", expanded=True):
        playerURL = st.text_input("Player's Transfermarkt Profile URL", value="")
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

    st.divider()
    # --- Player overview ---
    with st.container():
        st.markdown("### Key Information")

        country = playerInfo.get('countryBirth', '') or playerInfo.get('citizensip1') 
        # Compute DOB string and age safely (relative to transferDate)
        try:
            dob = date(playerInfo['yearBirth'], playerInfo['monthBirth'], playerInfo['dayBirth'])
            age_years = transferDate.year - dob.year - ((transferDate.month, transferDate.day) < (dob.month, dob.day))
            dob_str = dob.strftime('%d %b %Y')
        except Exception:
            age_years = None
            dob_str = "Unknown"

        st.markdown(f"##### {playerInfo.get('name', '')} [{country}] ({age_years if age_years is not None else '—'} yrs)")

        colA, colB, colC = st.columns([1, 2, 2])
        with colA:
            crest = playerInfo.get('clubImage')
            if crest:
                st.image(crest, use_container_width=False)
        with colB:
            st.markdown(f"**Club:** {playerInfo.get('currentClub', '')}")
            st.markdown(f"**League:** {playerInfo.get('currentLeague', '')}")           
        with colC:
            st.markdown(f"**League country:** {playerInfo.get('currentLeagueCountry', '')}")
            st.markdown(f"**Position:** {playerInfo.get('position', '')}")

    st.divider()

  
    ntInfo = pd.DataFrame(getNationalTeam(playerURL, transferDate))
    # st.write(ntInfo)
    # Show per-team metrics and table
    # for team in sorted(ntInfo['for'].unique()):
    #     team_df = ntInfo[(ntInfo['for'] == team) & (ntInfo['competitionID'] != 'FS')].copy()
    #     team_games = len(team_df)
    #     player_games = int(team_df['played'].sum()) if 'played' in team_df.columns else 0
    #     pct_played = (player_games / team_games * 100) if team_games else 0.0

    #     # st.subheader(team)
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.metric("Competitive Team matches", team_games)
        # with col2:
        #     st.metric("Player played", player_games)
        # with col3:
        #     st.metric("% of competitive matches", f"{pct_played:.1f}%")

    items = ['U21', 'U19', 'U18']
    unique_teams = list(ntInfo['for'].unique())
    final_teams = [team for team in unique_teams if all(item not in team for item in items)]
    # st.write(final_teams)

    if len(final_teams) > 0:
        x = fetch_fifa_rankings_timeseries(final_teams[0])
        rank = average_rank(x)

        team_df = ntInfo[(ntInfo['for'] == final_teams[0]) & (ntInfo['competitionID'] != 'FS')].copy()
        team_games = len(team_df)
        player_games = int(team_df['played'].sum()) if 'played' in team_df.columns else 0
        pct_played = (player_games / team_games) if team_games else 0.0

        # st.write(ntInfo['for'][0], "Average rank (last 30 months):", average_rank(x))

        if rank <=10:
            rankTarget = .30
            if pct_played >= rankTarget:
                st.success(f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 1-10 [ {rank} ]")
            elif pct_played >= .20:
                st.warning(f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 1-10 [ {rank} ] but they are close to meeting the auto-pass threshold")
            else:
                st.error(f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 1-10 [ {rank} ]")
        
        elif rank <=20:
            rankTarget = .40
            if pct_played >= rankTarget:
                st.success(f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 11-20 [ {rank} ]")
            elif pct_played >= .20:
                st.warning(f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 11-20 [ {rank} ] but they are close to meeting the auto-pass threshold")
            else:
                st.error(f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 11-20 [ {rank} ]")
        
        elif rank <=30:
            rankTarget = .60
            if pct_played >= rankTarget:
                st.success(f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 21–30 [ {rank} ]")
            elif pct_played >= .20:
                st.warning(f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 21–30 [ {rank} ] but they are close to meeting the auto-pass threshold")
            else:
                st.error(f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 21–30 [ {rank} ]")
        
        elif rank <=50:
            rankTarget = .70
            if pct_played >= rankTarget:
                st.success(f"AUTO-PASS GRANTED: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months for a team ranked between 31–50 [ {rank} ]")
            elif pct_played >= .20:
                st.warning(f"AUTO-PASS NEAR-MISS: The player has played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is just below the {rankTarget*100}% threshold for a team ranked between 31–50 [ {rank} ] but they are close to meeting the auto-pass threshold")
            else:
                st.error(f"AUTO-PASS FAIL: The player has only played {int(pct_played * 100)}% of competitive matches in the last 24 months, this is not above the {rankTarget*100}%  threshold for a team ranked between 31–50 [ {rank} ]")

        
        elif rank >50:
            st.error(f"AUTO-PASS FAIL: {final_teams[0]}'s FIFA Raking [{rank}] is below the auto-pass threshold of 50. Therefore the auto-pass criteria has not been met")

        else:
            st.warning(f"RANK UNDER CONSTRUCTION")

    else:
        st.error(f"AUTO-PASS FAIL: The player has not played for their {final_teams[0]}'s national team. Therefore the auto-pass criteria has not been met")





        # if 

        # st.table(team_df)

  
        
        # transferDate
        # day month year 
        # soupNationalTeam = get_souped_page(nationalTeamURL)
    # https://www.transfermarkt.co.uk/jude-bellingham/nationalmannschaft/spieler/581678/verein_id/3299/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2025&ende=27.08.2025&nurEinsatz=0 

# https://www.transfermarkt.co.uk/luka-hyrylainen/nationalmannschaft/spieler/716898/verein_id/20796/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2024&ende=28.08.2025&nurEinsatz=0
# https://www.transfermarkt.co.uk/luka-hyrylainen/nationalmannschaft/spieler/716898/verein_id/3299/plus/0?hauptwettbewerb=&wettbewerb_id=&trainer_id=&start=01.01.2024&ende=27.08.2025&nurEinsatz=0
if __name__ == "__main__":
    pass