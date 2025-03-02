import streamlit as st 

def navigation():
    pages = {
        "你的账户": [
            st.Page("change_name.py", title="修改用户名"),
            st.Page("change_pwd.py", title="修改密码"),
        ],
        "系统功能": [
            st.Page("text2sql.py", title="Text2SQL"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()