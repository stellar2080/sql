import os
import sqlite3
import streamlit as st

st.title("修改用户名")
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
        ROOT_PATH = os.environ["ROOT_PATH"]
        db_path = os.path.join(ROOT_PATH,'db','database.sqlite3')
        conn = sqlite3.connect(database=db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM user_data WHERE username = ?',
                    (new_username,))
        result = cursor.fetchone()
        if result:
            st.error("用户名已存在")
        else:
            cursor.execute("UPDATE user_data set username = ? WHERE username = ?", 
                        (new_username,username))
            st.session_state.username = new_username
            conn.commit()
            st.success("修改用户名成功")