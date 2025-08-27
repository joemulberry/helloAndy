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

    # ------- get soup -------- #

    url = 'https://www.transfermarkt.co.uk/jude-bellingham/profil/spieler/581678'
    soup = get_souped_page(url)

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

    for li in infoRaw: 
        if 'Place of birth:' in li.text:
            store['placeBirth'] = li.text.split(':')[1].strip()
            store['countryBirth'] = li.find('img')['title']
            
    for li in infoRaw: 
        if 'Citizenship' in li.text:   
            if len(li.find_all('img')) == 1:                     
                store['citizensip1'] = li.find_all('img')[0]['title']
                store['citizensip2'] = None
            elif len(li.find_all('img')) == 2:                     
                store['citizensip2'] = li.find_all('img')[1]['title']
            else:
                store['citizensip1'] = None
                store['citizensip2'] = None

    for li in infoRaw: 
        if 'Height' in li.text:  
            store['height'] = int(li.text.split(':')[1].strip().replace(',','').replace('m', '').strip())

    
    for li in infoRaw: 
        if 'Position' in li.text: 
            store['position'] = li.text.split(':')[1].strip() 

    for li in infoRaw: 
        if 'Current international:' in li.text: 
            store['nationalTeam'] = li.find('img')['title']

    for li in infoRaw: 
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


    store['leagueInfo'] = leagueInfo
    store['bigbox'] = bigBox

    return store


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

    playerURL = st.text_input('playerURL', value="", max_chars=None, key=None)

    if playerURL != "":
        st.write(playerURL)
        playerInfo = parsePlayer(playerURL)
        st.write(playerInfo)
    

if __name__ == "__main__":
    pass