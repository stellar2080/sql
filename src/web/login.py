import os
import streamlit as st
import bcrypt
import sqlite3

def login():
    st.title("用户登录")
    user = st.text_input(label="用户名/邮箱")
    password = st.text_input(label="密码", type="password", max_chars=16)
    col0, col1 = st.columns([1,1], vertical_alignment='top')
    with col0:    
        submit = st.button(label="登录", use_container_width=True)
    with col1:
        register = st.button(label="注册", use_container_width=True)
    if submit:
        if user == "":
            st.error("用户名/邮箱不能为空")
        elif password == "":
            st.error("密码不能为空")
        elif " " in user:
            st.error("用户名/邮箱不能含有空格")
        elif " " in password:
            st.error("密码不能含有空格")
        else:
            ROOT_PATH = os.environ["ROOT_PATH"]
            db_path = os.path.join(ROOT_PATH,'db','database.sqlite3')
            conn = sqlite3.connect(database=db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM user_data WHERE username = ?',(user,))
            user_result = cursor.fetchone() 
            cursor.execute('SELECT username, password FROM user_data WHERE email = ?',(user,))
            email_result = cursor.fetchone()           
            if user_result:
                stored_hashed_password = user_result[0]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    st.session_state.logged_in = True
                    st.session_state.page = "navigation"
                    st.session_state.username = user
                    st.success(f"登录成功，欢迎回来，{user}")
                    st.rerun()
                else:
                    st.error("密码错误")
            elif email_result:
                username = email_result[0]
                stored_hashed_password = email_result[1]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    st.session_state.logged_in = True
                    st.session_state.page = "navigation"
                    st.session_state.username = username
                    st.success(f"登录成功，欢迎回来，{username}")
                    st.rerun()
                else:
                    st.error("密码错误")
            else:
                st.error("用户名/邮箱不存在")
            
    if register:
        st.session_state.page = "register"
        st.rerun()
        

