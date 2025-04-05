import asyncio
import datetime
import string
import random
import bcrypt
import reflex as rx
from sqlmodel import select

from client.utils.email_utils import send_email, validate_email
from client.db_model import User, Settings, AIConfig

class SignupState(rx.State):
    email: str = ""
    send_time: datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
    countdown: int = 0
    captcha: str = None

    @rx.event
    def set_email(self, email: str):
        self.email = email
    
    @rx.event
    def reset_countdown(self):
        self.countdown = 0

    @rx.event
    def generate_id(self, length=8):
        characters = string.digits + string.ascii_letters
        return ''.join(random.choice(characters) for _ in range(length))

    @rx.event
    def send_email(self): 
        if self.email == "":
            return rx.toast.error("邮箱不能为空", duration=2000)
        elif not validate_email(email=self.email):
            return rx.toast.error("邮箱格式错误", duration=2000)
        with rx.session() as session:
            if session.exec(select(User).where(User.email == self.email)).first():
                return rx.toast.error("邮箱已被注册", duration=2000)
        self.send_time = datetime.datetime.now()
        self.captcha = send_email(msg_to=self.email)
        print(self.captcha)
        yield rx.toast.success("验证码发送成功", duration=2000)
        return SignupState.count

    @rx.event(background=True)
    async def count(self):
        async with self:
            self.countdown = 60
        while True:
            async with self:
                if self.countdown <= 0:
                    return
                self.countdown -= 1
            await asyncio.sleep(1)

    @rx.event
    def signup(self,form_data: dict):
        username = form_data.get('username','')
        email = form_data.get('email','')
        captcha = form_data.get('captcha','')
        password = form_data.get('password','')
        confirm_password = form_data.get('confirm_password','')
        if username == "" or password == "" or email == "" or \
            captcha=="" or confirm_password=="":
            return rx.toast.error("请填写所有信息", duration=2000)
        if " " in username:
            return rx.toast.error("用户名不能含有空格", duration=2000)
        if len(username) < 6 or len(username) > 10:
            return rx.toast.error("用户名长度应在6位到10位间", duration=2000)
        if " " in password:
            return rx.toast.error("密码不能含有空格", duration=2000)
        if len(password) < 8 or len(password) > 15:
            return rx.toast.error("密码长度应在8位到15位间", duration=2000)
        if not validate_email(email=email):
            return rx.toast.error("邮箱格式错误", duration=2000)
        if password != confirm_password:
            return rx.toast.error("密码与确认密码需完全相同", duration=2000)
        if self.email != email or self.captcha != captcha:
            return rx.toast.error("验证码错误", duration=2000)
        if (datetime.datetime.now() - self.send_time).total_seconds() > 300:
            return rx.toast.error("验证码已过期", duration=2000)
        with rx.session() as session:
            if session.exec(select(User).where(User.username == username)).first():
                return rx.toast.error("用户名已存在", duration=2000)
            if session.exec(select(User).where(User.email == email)).first():
                return rx.toast.error("邮箱已被注册", duration=2000)
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            print(hashed_password)
            random_id = self.generate_id()
            user = User(
                user_id=random_id, username=username, email=email, password=hashed_password
            )
            settings = Settings(
                user_id=random_id, 
                accent_color = "violet", 
                gray_color = "gray",
                radius = "large",
                scaling = "100%",
            )
            ai_config = AIConfig(
                user_id=random_id,
                platform = 'Tongyi',
                model = 'deepseek-v3',
                api_key='',
                LLM_HOST = 'localhost',
                LLM_PORT = 6006,
                MAX_ITERATIONS = 3,
                DO_SAMPLE = False,
                TEMPERATURE = 0.1,
                TOP_P = 0.1,
                MAX_TOKENS = 8192,
                N_RESULTS = 3,
                E_HINT_THRESHOLD = 0.30,
                E_COL_THRESHOLD = 0.30,
                E_VAL_THRESHOLD = 0.30,
                E_COL_STRONG_THRESHOLD = 0.48,
                E_VAL_STRONG_THRESHOLD = 0.48,
                F_HINT_THRESHOLD = 0.80,
                F_COL_THRESHOLD = 0.60,
                F_LSH_THRESHOLD = 0.40,
                F_VAL_THRESHOLD = 0.60,
                F_COL_STRONG_THRESHOLD = 0.85,
                F_VAL_STRONG_THRESHOLD = 0.85,
                G_HINT_THRESHOLD = 0.30,
            )
            session.add(user)
            session.add(settings)
            session.add(ai_config)
            session.commit()
        self.reset_countdown()
        self.email = ""
        yield rx.toast.success("注册成功，已返回登录页面", duration=2000)
        return rx.redirect("/login")
