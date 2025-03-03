from datetime import datetime
import os
import sqlite3
import bcrypt
import streamlit as st

ROOT_PATH = os.environ["ROOT_PATH"]
db_path = os.path.join(ROOT_PATH,'db','database.sqlite3')
conn = sqlite3.connect(database=db_path,
                        check_same_thread=False)

from src.utils.email_utils import send_email,validate_email

if 'send_time' not in st.session_state:
    epoch = datetime(1970, 1, 1, 0, 0, 0)
    st.session_state.send_time = epoch

@st.dialog("修改用户名",width="large")
def change_username():
    username = st.session_state.username
    new_username = st.text_input(label="新用户名", type="password", max_chars=10)
    submit = st.button(label="更改用户名", use_container_width=True)
    if submit:
        if new_username == "":
            st.error("新用户名不能为空")
        elif " " in new_username:
            st.error("新用户名不能含有空格")
        elif username == new_username:
            st.error("新用户名不能和原用户名相同")
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM user_data WHERE username = ?',
                        (new_username,))
            result = cursor.fetchone()
            if result:
                st.error("用户名已存在")
            else:
                cursor.execute("UPDATE user_data set username = ? WHERE username = ?", 
                            (new_username,username))
                conn.commit()
                st.session_state.username = new_username
                st.success("修改用户名成功")
                st.rerun()

@st.dialog("修改邮箱",width="large")
def change_email():
    username = st.session_state.username
    email = st.session_state.email
    new_email = st.text_input(label="新邮箱")
    col0,col1 = st.columns([2,1],vertical_alignment="bottom")
    with col0:
        captcha = st.text_input(label="验证码")
    with col1:
        send = st.button(label="发送验证码", use_container_width=True)
    submit = st.button(label="更改邮箱", use_container_width=True)
    if send:
        elapsed = int(
            (datetime.now() - st.session_state.send_time).total_seconds()
        )
        if new_email == "":
            st.error("邮箱不能为空")
        elif not validate_email(email=new_email):
            st.error("邮箱格式错误")
        elif new_email == email:
            st.error("新邮箱不能与原邮箱相同")
        elif elapsed < 60:
            st.error(f"等待{60 - elapsed}秒后才能再次发送验证码")
        else:
            sent_captcha = send_email(msg_to=new_email)
            send_time = datetime.now()
            st.session_state.send_time = send_time
            cursor = conn.cursor()
            cursor.execute('INSERT INTO captcha_record(email,captcha,send_time) VALUES(?,?,?)',
                        (new_email,sent_captcha,send_time))
            conn.commit()
            st.success("验证码发送成功，请注意查收")
    if submit:
        if new_email == "":
            st.error("新邮箱不能为空")
        elif not validate_email(email=new_email):
            st.error("邮箱格式错误")
        elif new_email == email:
            st.error("新邮箱不能与原邮箱相同")
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT captcha, send_time FROM captcha_record WHERE email = ? ORDER BY send_time DESC LIMIT 1',
                            (new_email,))
            captcha_result = cursor.fetchone()
            if not captcha_result:
                st.error("未查询到验证码发送记录")
            else:
                record_captcha = captcha_result[0]
                record_send_time = datetime.strptime(captcha_result[1], "%Y-%m-%d %H:%M:%S.%f")
                now_time = datetime.now()
                timediff = now_time - record_send_time
                if record_captcha != captcha:
                    st.error("验证码错误")
                elif timediff.total_seconds() > 300:
                    st.error("验证码已过期")
                else:
                    cursor.execute('SELECT email FROM user_data WHERE email = ?',(new_email,))
                    result = cursor.fetchone()
                    if result:
                        st.error("该邮箱已被使用")
                    else:
                        cursor.execute("UPDATE user_data set email = ? WHERE username = ?", 
                                    (new_email,username))
                        conn.commit()
                        st.session_state.email = new_email
                        st.success("修改邮箱成功")
                        st.rerun()

@st.dialog("修改密码",width="large")
def change_pwd():
    username = st.session_state.username
    new_password = st.text_input(label="新密码", type="password", max_chars=16)
    confirm_password = st.text_input(label="确认密码", type="password", max_chars=16)
    submit = st.button(label="更改密码", use_container_width=True)
    if submit:
        if new_password == "":
            st.error("新密码不能为空")
        elif " " in new_password:
            st.error("新密码不能含有空格")
        elif new_password != confirm_password:
            st.error("新密码与确认密码需完全相同")
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT username,password FROM user_data WHERE username = ?',(username,))
            result = cursor.fetchone()
            if result:
                stored_hashed_password = result[1]
                if bcrypt.checkpw(new_password.encode('utf-8'), stored_hashed_password):
                    st.error("新密码不能与原密码相同")
                else:
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
                    cursor.execute("UPDATE user_data set password = ? WHERE username = ?", 
                                (hashed_password,username))
                    conn.commit()
                    st.session_state.password = new_password
                    st.success("修改密码成功")
                    st.rerun()
            else:
                st.error("用户名不存在")

st.title("账户信息")
username = st.session_state.username
email = st.session_state.email
password = st.session_state.password
col0, col1 = st.columns([3,1],vertical_alignment="bottom")
with col0:
    st.text_input(label="用户名",value=username,disabled=True)
with col1:
    if st.button("修改用户名",use_container_width=True):
        change_username()
col2, col3 = st.columns([3,1],vertical_alignment="bottom")
with col2:
    st.text_input(label="邮箱",value=email,disabled=True)
with col3:
    if st.button("修改邮箱",use_container_width=True):
        change_email()
col4, col5 = st.columns([3,1],vertical_alignment="bottom")
with col4:
    st.text_input(label="密码",value=password,type="password",disabled=True)
with col5:
    if st.button("修改密码",use_container_width=True):
        change_pwd()