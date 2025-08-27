import streamlit as st
from datetime import datetime

APP_PASSWORD = "letmein"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

password = st.text_input("Enter password", type="password")

if password:
    if password == APP_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.error("Wrong password, try again.")

if st.session_state.authenticated:
    st.set_page_config(page_title="Hello Streamlit", page_icon="👋", layout="centered")

    st.title("Hello, Streamlit 👋")
    st.write("This is a bare-bones app. Use the sidebar to interact.")

    with st.sidebar:
        st.header("Controls")
        name = st.text_input("Your name", "")
        show_time = st.checkbox("Show current time")

    if name:
        st.success(f"Welcome, {name}!")

    if show_time:
        st.info(f"Current time: {datetime.now():%Y-%m-%d %H:%M:%S}")

    uploaded = st.file_uploader("Upload a CSV to preview", type=["csv"])
    if uploaded is not None:
        import pandas as pd
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())

    st.caption("Built with Streamlit · minimal example")

if __name__ == "__main__":
    pass