import streamlit as st
from datetime import datetime, date
import pandas as pd 
from bs4 import BeautifulSoup
from random import choice 
import requests 

from internationalMatches import international_appearance_points
from fifaPull import fetch_fifa_rankings_timeseries, average_rank
from utils import * 
from parse import parsePlayer
from autoPass import autoPass


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
                st.image(crest, width='content')
        with colB:
            st.markdown(f"**Club:** {playerInfo.get('currentClub', '')}")
            st.markdown(f"**League:** {playerInfo.get('currentLeague', '')}")           
        with colC:
            st.markdown(f"**League country:** {playerInfo.get('currentLeagueCountry', '')}")
            st.markdown(f"**Position:** {playerInfo.get('position', '')}")

    st.divider()

  
    ntInfo = pd.DataFrame(getNationalTeam(playerURL, transferDate))
    items = ['U21', 'U19', 'U18']
    unique_teams = list(ntInfo['for'].unique())
    seniorNationalTeam = [team for team in unique_teams if all(item not in team for item in items)]
    if len(seniorNationalTeam) >0:
        seniorNationalTeamID = ntInfo[ntInfo['for'] == seniorNationalTeam[0]].reset_index().iloc[0]['teamID']
        seniorNationalTeam = seniorNationalTeam[0]
    else: 
        seniorNationalTeamID = None
        seniorNationalTeam = None

    st.write(seniorNationalTeam, seniorNationalTeamID)

    if seniorNationalTeam != None:
        
        today_year = date.today().year
        years = [today_year - 2, today_year - 1, today_year]
        
        year = years[0] 
        seniorURL = 'https://www.transfermarkt.co.uk/' + seniorNationalTeam + '/spielplan/verein/' + seniorNationalTeamID + '/plus/0?saison_id=' + str(year)
        st.write(seniorURL)

    # st.write(ntInfo)
    # st.write(ntInfo)
    # items = ['U21', 'U19', 'U18']
    # unique_teams = list(ntInfo['for'].unique())
    # final_teams = [team for team in unique_teams if all(item not in team for item in items)]
    # # st.write(final_teams)

    # dd = {'internationalPoints' : 0 }
    # st.write({"nt_rows": len(ntInfo), "unique_teams": ntInfo['for'].unique().tolist(), "final_teams": final_teams})
    
    # if len(final_teams) > 0:
    #     x = fetch_fifa_rankings_timeseries(final_teams[0])
    #     rank = average_rank(x)
    #     team_df = ntInfo[(ntInfo['for'] == final_teams[0]) & (ntInfo['competitionID'] != 'FS')].copy()
    #     team_games = len(team_df)
    #     player_games = int(team_df['played'].sum()) if 'played' in team_df.columns else 0
    #     pct_played = (player_games / team_games) if team_games else 0.0
        

    #     # print('FUNCTION TRIGGERED')
    #     # try:
    #     dd["internationalPoints"] = international_appearance_points(rank, pct_played)
    #     # except Exception as e:
    #     #     st.error(f"international_appearance_points failed: {e}")
    #     #     # dd['internationalPoints'] = international_appearance_points(rank,pct_played)

    #     # st.write(ntInfo['for'][0], "Average rank (last 30 months):", average_rank(x))
    #     autoPassResult, autoPassText = autoPass(rank, pct_played, final_teams)
        

    # else:
    #     autoPassResult = 0
    #     autoPassText = f"AUTO-PASS FAIL: The player has not played for their {final_teams[0]}'s national team. Therefore the auto-pass criteria has not been met"

    # st.header('GBE Eligibility')
    # st.subheader('AutoPass')
    # if autoPassResult == 1:
    #     st.badge("Auto-Pass Obtained", icon=":material/check:", color="green")
    #     st.badge("Auto-Pass Not Granted", icon=":material/dangerous:", color="red")
    #     st.badge("Auto-Pass Nearly Granted", icon=":material/error:", color="orange")
    #     st.text(autoPassText)
    # elif autoPassResult == 2:
    #     st.badge("Auto-Pass Nearly Granted", icon=":material/error:", color="orange")
    #     st.text(autoPassText)
    # else: 
    #     st.badge("Auto-Pass Not Granted", icon=":material/dangerous:", color="red")
    #     st.text(autoPassText)
    # st.write(autoPassResult, autoPassText)


    # st.write('international points', dd['internationalPoints'])



if __name__ == "__main__":
    pass