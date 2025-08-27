import streamlit as st
from datetime import datetime
import pandas as pd 

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
    

if __name__ == "__main__":
    pass