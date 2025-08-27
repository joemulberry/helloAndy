import streamlit as st
from datetime import datetime
import pandas as pd 
from bs4 import BeautifulSoup
from random import choice 
import requests 


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


    store['labels'] = labels

    return store

def _on_player_url_change():
    url = st.session_state.get('playerURL', '')
    if url:
        st.session_state['playerInfo'] = parsePlayer(url)

st.set_page_config(page_title="GBE ESC Checker", page_icon="👋", layout="centered", initial_sidebar_state="expanded")

APP_PASSWORD = "letmein"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.sidebar:
        st.header("Login")
        password = st.text_input("Enter password", type="password")
    if password:
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
        else:
            st.error("Wrong password, try again.")

if st.session_state.authenticated:
    st.title('GBE/ESC Checker')

    st.text_input('playerURL', value="", key='playerURL', on_change=_on_player_url_change)

    if 'playerInfo' in st.session_state:
        st.write(st.session_state['playerURL'])
        st.write(st.session_state['playerInfo'])
    

if __name__ == "__main__":
    pass