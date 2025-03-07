import streamlit as st
import bcrypt

@st.dialog("系统消息")
def login_success(username):
    st.write(f"登录成功，欢迎回来，{username}")
    if st.button("确定",use_container_width=True):
        st.session_state.page = "navigation"
        st.rerun()

def login():
    st.title("用户登录")
    user = st.text_input(label="用户名/邮箱")
    col0, col1 = st.columns([2,1], vertical_alignment='bottom')
    with col0:
        password = st.text_input(label="密码", type="password", max_chars=16)
    with col1:
        forget_pwd = st.button(label="找回密码", use_container_width=True)
    col2, col3 = st.columns([1,1], vertical_alignment='top')
    with col2:    
        register = st.button(label="注册", use_container_width=True)
    with col3:
        submit = st.button(label="登录", use_container_width=True)
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
            conn = st.session_state.conn
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, email, password FROM user_data WHERE username = ?',(user,))
            user_result = cursor.fetchone() 
            cursor.execute('SELECT user_id, username, password FROM user_data WHERE email = ?',(user,))
            email_result = cursor.fetchone()        
            if user_result:
                user_id = user_result[0]
                email = user_result[1]
                stored_hashed_password = user_result[2]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    st.session_state.user_id = user_id
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.email = email
                    st.session_state.password = password
                    login_success(user)
                else:
                    st.error("密码错误")
            elif email_result:
                user_id = email_result[0]
                username = email_result[1]
                stored_hashed_password = email_result[2]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    st.session_state.user_id = user_id
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.email = user
                    st.session_state.password = password
                    login_success(username)
                else:
                    st.error("密码错误")
            else:
                st.error("用户名/邮箱不存在")
            
    if register:
        st.session_state.page = "register"
        st.rerun()
        
    if forget_pwd:
        st.session_state.page = "forget_pwd"
        st.rerun()

