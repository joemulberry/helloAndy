import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Hello Streamlit", page_icon="👋", layout="centered", initial_sidebar_state="expanded")

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
    st.title('GBE/ESC Checkerrr')

    st.title("Hello, Streamlit 👋")
    st.write("This is a bare-bones app.")

    uploaded = st.file_uploader("Upload a CSV to preview", type=["csv"])
    if uploaded is not None:
        import pandas as pd
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())

    st.caption("Built with Streamlit · minimal example")

    # Ensure the sidebar is empty when authenticated (no widgets shown)
    st.sidebar.empty()

if __name__ == "__main__":
    pass