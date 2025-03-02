import streamlit as st 
import os
import pandas as pd
import numpy as np

from src.manager.manager import Manager
os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"
os.environ["DEEPSEEK_API_KEY"] = "sk-46d3e1d50d704b15a53421dbb7e4ab6a"
ROOT_PATH = os.environ["ROOT_PATH"]

# manager = Manager(
#     config={
#         'platform': 'Api',
#         'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
#         'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
#         'vectordb_client': 'http',
#         'vectordb_host': 'localhost',
#         'vectordb_port': '8000'
#     },
# )

st.title('TEXT2SQL')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]) as role_message:
        if message["role"] == "user" or message["role"] == "human":
            st.write(message["content"])
        elif message["role"] == "ai" or message["role"] == "assistant":
            st.write('以下是SQL查询结果：')
            st.table(message["content"])

if question := st.chat_input("请输入你的问题："):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user") as user_message:
        st.write(question)

    # message = manager.chat(question=question)
    # sql_result = message['sql_result']
    # col_names = sql_result['cols']
    # rows = sql_result['rows']
    # df = pd.DataFrame(rows, columns=col_names)
    df = pd.DataFrame(np.random.randn(3,3))

    st.session_state.messages.append({"role": "assistant", "content": df})
    with st.chat_message("assistant"):
        st.write('以下是SQL查询结果：')
        st.table(df)