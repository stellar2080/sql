from datetime import datetime
import os
import sqlite3
import subprocess
import sys
import time
import psutil
import requests
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(ROOT_PATH)
os.environ["ROOT_PATH"] = ROOT_PATH
os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"
os.environ["DEEPSEEK_API_KEY"] = "sk-46d3e1d50d704b15a53421dbb7e4ab6a"

from register import register
from login import login
from forget_pwd import forget_pwd
from src.manager.manager import Manager

def find_and_kill_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            connections = proc.net_connections()
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    print(f"Found process {proc.info['name']} (PID: {proc.info['pid']}) using port {port}")
                    proc.kill()
                    print(f"Process {proc.info['name']} (PID: {proc.info['pid']}) has been terminated.")
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"No process found using port {port}")

def wait_for_chroma(port, timeout=15):
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"http://localhost:{port}/api/v1/heartbeat")
            if response.status_code == 200:
                print("检测到 Chroma 服务已启动")
                return True
        except requests.exceptions.ConnectionError:
            pass
        if time.time() - start_time > timeout:
            print("等待 Chroma 服务启动超时")
            return False
        time.sleep(1)

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

if __name__ == '__main__':
    vectordb_path = os.path.join(ROOT_PATH,'vectordb')
    log_path = os.path.join(vectordb_path, 'chroma.log')
    db_path = os.path.join(ROOT_PATH,'db','database.sqlite3')
    if 'started_vectordb' not in st.session_state:
        st.session_state.started_vectordb = True
        find_and_kill_process_by_port(8000)
        os.makedirs(vectordb_path, exist_ok=True)
        subprocess.Popen(['chroma', 'run', '--path', f'{vectordb_path}', '--log-path', f'{log_path}'])
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'conn' not in st.session_state:
        st.session_state.conn = sqlite3.connect(database=db_path, check_same_thread=False)
    if 'send_time' not in st.session_state:
        epoch = datetime(1970, 1, 1, 0, 0, 0)
        st.session_state.send_time = epoch
    if "manager" not in st.session_state:
        if wait_for_chroma(8000):
            manager = Manager(
                config={
                    'platform': 'Api',
                    'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
                    'vectordb_path': vectordb_path,
                    'vectordb_client': 'http',
                    'vectordb_host': 'localhost',
                    'vectordb_port': '8000'
                },
            )
            st.session_state.manager = manager
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.set_page_config(
        page_title='TEXT2SQL',
        page_icon='♾️',
        layout='wide'
    )
    if st.session_state.page == "login":
        login()
    if st.session_state.page == "register":
        register()
    if st.session_state.page == "forget_pwd":
        forget_pwd()
    if st.session_state.page == "navigation":
        navigation()