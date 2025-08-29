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
    # print(nationalTeamURL)
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
        
        print('/////////', nationalTeamURLSubSection)
        
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
            