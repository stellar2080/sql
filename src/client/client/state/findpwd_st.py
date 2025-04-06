import asyncio
import datetime
import bcrypt
import reflex as rx
from sqlmodel import select

from client.utils.email_utils import send_email, validate_email
from client.db_model import User

class FindpwdState(rx.State):
    email: str = ""
    send_time: datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
    countdown: int = 0
    captcha: str = None

    @rx.event
    def set_email(self, email: str):
        self.email = email

    def reset_vars(self):
        self.email_sent = ""
        self.send_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.countdown = 0
        self.captcha = None

    @rx.event
    def send_email(self):
        if self.email == "":
            return rx.toast.error("邮箱不能为空", duration=2000)
        if not validate_email(email=self.email):
            return rx.toast.error("邮箱格式错误", duration=2000)
        with rx.session() as session:
            if not session.exec(
                select(User).where(
                    User.email == self.email
                    )
                ).first():
                return rx.toast.error("邮箱未被使用", duration=2000)
            self.send_time = datetime.datetime.now()
            self.captcha = send_email(msg_to=self.email)
            print(self.captcha)
            yield rx.toast.success("验证码发送成功", duration=2000)
            return FindpwdState.count

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
    def change_pwd(self,form_data: dict):
        email = form_data.get('email','')
        captcha = form_data.get('captcha','')
        password = form_data.get('password','')
        confirm_password = form_data.get('confirm_password','')
        if email == "" or captcha == "" or password == "" or confirm_password == "":
            return rx.toast.error("请填写所有信息", duration=2000)
        if " " in password:
            return rx.toast.error("密码不能含有空格", duration=2000)
        if not validate_email(email=email):
            return rx.toast.error("邮箱格式错误", duration=2000)
        if password != confirm_password:
            return rx.toast.error("密码与确认密码需完全相同", duration=2000)
        if len(password) < 8 or len(password) > 15:
            return rx.toast.error("密码长度应在8位到15位间", duration=2000)
        if self.email != email or self.captcha != captcha:
            return rx.toast.error("验证码错误", duration=2000)
        if (datetime.datetime.now() - self.send_time).total_seconds() > 300:
            return rx.toast.error("验证码已过期", duration=2000)
        with rx.session() as session:   
            user = session.exec(
                User.select().where(
                    User.email == email
                )
            ).first()
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            print(hashed_password)
            user.password = hashed_password
            session.add(user)
            session.commit()
        self.reset_vars()
        yield rx.toast.success("修改密码成功，返回登录页面", duration=2000)
        return rx.redirect("/login")
