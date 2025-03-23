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

    findpwd_dialog_description: str = ""
    findpwd_dialog_open: bool = False
    findpwdsuccess_dialog_open: bool = False

    @rx.event
    def findpwd_dialog_open_change(self):
        self.findpwd_dialog_open = not self.findpwd_dialog_open

    @rx.event
    def findpwdsuccess_dialog_open_change(self):
        self.findpwdsuccess_dialog_open = not self.findpwdsuccess_dialog_open

    @rx.event
    def findpwd_success_redirect(self):
        self.findpwdsuccess_dialog_open_change()
        return rx.redirect("/login")

    @rx.event
    def set_email(self, email: str):
        self.email = email

    @rx.event
    def reset_countdown(self):
        self.countdown = 0

    @rx.event
    def send_email(self):
        if self.email == "":
            self.findpwd_dialog_description = "邮箱不能为空"
            return self.findpwd_dialog_open_change()
        if not validate_email(email=self.email):
            self.findpwd_dialog_description = "邮箱格式错误"
            return self.findpwd_dialog_open_change()
        with rx.session() as session:
            if not session.exec(
                select(User).where(
                    User.email == self.email
                    )
                ).first():
                self.findpwd_dialog_description = "邮箱不存在"
                return self.findpwd_dialog_open_change()
            self.send_time = datetime.datetime.now()
            self.captcha = send_email(msg_to=self.email)
            print(self.captcha)
            self.findpwd_dialog_description = "验证码发送成功!"
            self.findpwd_dialog_open_change()
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
            self.findpwd_dialog_description = "请填写所有信息"
            return self.findpwd_dialog_open_change()
        if " " in password:
            self.findpwd_dialog_description = "密码不能含有空格"
            return self.findpwd_dialog_open_change()
        if not validate_email(email=email):
            self.findpwd_dialog_description = "邮箱格式错误"
            return self.findpwd_dialog_open_change()
        if password != confirm_password:
            self.findpwd_dialog_description = "密码与确认密码需完全相同"
            return self.findpwd_dialog_open_change()
        if self.email != email or self.captcha != captcha:
            self.findpwd_dialog_description = "验证码错误"
            return self.findpwd_dialog_open_change()
        if (datetime.datetime.now() - self.send_time).total_seconds() > 300:
            self.findpwd_dialog_description = "验证码已过期"
            return self.findpwd_dialog_open_change()
        with rx.session() as session:   
            user = session.exec(
                User.select().where(
                    (User.email == email)
                )
            ).first()
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            print(hashed_password)
            user.password = hashed_password
            session.add(user)
            session.commit()
        self.reset_countdown()
        self.findpwd_dialog_description = "修改密码成功，点击确定返回登录页面"   
        return self.findpwdsuccess_dialog_open_change()
