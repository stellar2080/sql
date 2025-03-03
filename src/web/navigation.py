import os
import streamlit as st 

from src.manager.manager import Manager
os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"
os.environ["DEEPSEEK_API_KEY"] = "sk-46d3e1d50d704b15a53421dbb7e4ab6a"
ROOT_PATH = os.environ["ROOT_PATH"]

manager = Manager(
    config={
        'platform': 'Api',
        'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'vectordb_client': 'http',
        'vectordb_host': 'localhost',
        'vectordb_port': '8000'
    },
)
if "manager" not in st.session_state:
    st.session_state.manager = manager

def navigation():
    pages = {
        "系统功能": [
            st.Page("text2sql.py", title="Text2SQL"),
            st.Page("repository.py", title="知识库"),
        ],
        "账户": [
            st.Page("account.py", title="账户信息"),
        ]
    }
    pg = st.navigation(pages)
    pg.run()