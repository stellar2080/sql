import os
import sqlite3
import bcrypt
import streamlit as st

st.title("修改密码")
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
        ROOT_PATH = os.environ["ROOT_PATH"]
        conn = sqlite3.connect(database=os.path.join(ROOT_PATH,'db','database.sqlite3'))
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
                st.success("修改密码成功")
        else:
            st.error("用户名不存在")