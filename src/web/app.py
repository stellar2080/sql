import os
import sys
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(os.path.dirname(current_dir))
os.environ["ROOT_PATH"] = ROOT_PATH
sys.path.append(ROOT_PATH)

from register import register
from login import login
from navigation import navigation

if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

if __name__ == '__main__':
    st.set_page_config(
        page_title='TEXT2SQL',
        page_icon='♾️',
        layout='wide'
    )
    if st.session_state.page == "login":
        login()
    if st.session_state.page == "register":
        register()
    if st.session_state.page == "navigation":
        navigation()