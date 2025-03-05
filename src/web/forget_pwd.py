import streamlit as st
import bcrypt
from datetime import datetime
from src.utils.email_utils import send_email, validate_email

@st.dialog("系统消息")
def change_pwd_success():
    st.write("修改密码成功，点击确定返回登录界面")
    if st.button("确定",use_container_width=True):
        st.session_state.page="login"
        st.rerun()

def forget_pwd():
    if 'send_time' not in st.session_state:
        epoch = datetime(1970, 1, 1, 0, 0, 0)
        st.session_state.send_time = epoch
    conn = st.session_state.conn

    st.title("找回密码")
    email = st.text_input(label="邮箱")
    col0, col1 = st.columns([2,1], vertical_alignment='bottom')
    with col0:
        captcha = st.text_input(label="验证码")
    with col1:
        send = st.button(label="发送验证码", use_container_width=True)
    password = st.text_input(label="新密码", type="password", max_chars=16)
    confirm_password = st.text_input(label="确认密码", type="password", max_chars=16)    
    col3, col4 = st.columns([1,1], vertical_alignment='top')
    with col3:
        back = st.button(label="返回", use_container_width=True)   
    with col4:
        submit = st.button(label="确认", use_container_width=True)
    if send:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM user_data WHERE email = ?',
                        (email,))
        email_result = cursor.fetchone()
        elapsed = int(
            (datetime.now() - st.session_state.send_time).total_seconds()
        )
        if not email_result:
            st.error("该邮箱未被注册")
        if email == "":
            st.error("邮箱不能为空")
        elif not validate_email(email=email):
            st.error("邮箱格式错误")
        elif elapsed < 60:
            st.error(f"等待{60 - elapsed}秒后才能再次发送验证码")
        else:
            sent_captcha = send_email(msg_to=email)
            send_time = datetime.now()
            st.session_state.send_time = send_time
            cursor = conn.cursor()
            cursor.execute('INSERT INTO captcha_record(email,captcha,send_time) VALUES(?,?,?)',
                        (email,sent_captcha,send_time))
            conn.commit()
            st.success("验证码发送成功，请注意查收")
    if submit:
        if password == "":
            st.error("密码不能为空")
        elif email == "":
            st.error("邮箱不能为空")
        elif " " in password:
            st.error("密码不能含有空格")
        elif not validate_email(email=email):
            st.error("邮箱格式错误")
        elif password != confirm_password:
            st.error("新密码与确认密码需完全相同")
        else:
            cursor = conn.cursor()
            cursor.execute('''SELECT captcha, send_time FROM captcha_record WHERE email = ? 
                           ORDER BY send_time DESC LIMIT 1''',
                            (email,))
            captcha_result = cursor.fetchone()
            if not captcha_result:
                st.error("未查询到该邮箱的验证码发送记录")
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
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
                    cursor.execute("UPDATE user_data set password = ? WHERE email = ?", 
                                (hashed_password,email))
                    conn.commit()
                    change_pwd_success()

    elif back:
        st.session_state.page = "login"
        st.rerun()