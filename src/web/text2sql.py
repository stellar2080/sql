import streamlit as st 
import pandas as pd
import numpy as np

st.title('Text2SQL')

if "messages" not in st.session_state:
    st.session_state.messages = []
manager = st.session_state.manager

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