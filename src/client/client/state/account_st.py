import asyncio
import datetime
import bcrypt
import reflex as rx
from sqlmodel import select

from client.utils.email_utils import send_email, validate_email
from client.db_model import User
from .base_st import BaseState

class AccountState(BaseState):
    email_sent: str = ""
    send_time: datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
    countdown: int = 0
    captcha: str = None

    account_dialog_open: bool = False
    success_dialog_open: bool = False
    change_username_dialog_open: bool = False
    change_email_dialog_open: bool = False
    change_password_dialog_open: bool = False

    @rx.event
    def on_load(self):
        if not self.logged_in:
            return rx.redirect("/login")

    @rx.event
    def account_dialog_open_change(self):
        self.account_dialog_open = not self.account_dialog_open

    @rx.event
    def success_dialog_open_change(self):
        self.success_dialog_open = not self.success_dialog_open

    @rx.event
    def change_username_dialog_open_change(self):
        self.change_username_dialog_open = not self.change_username_dialog_open

    @rx.event
    def change_email_dialog_open_change(self):
        self.change_email_dialog_open = not self.change_email_dialog_open

    @rx.event
    def change_password_dialog_open_change(self):
        self.change_password_dialog_open = not self.change_password_dialog_open

    @rx.event
    def close_all_dialog(self):
        self.account_dialog_open = False
        self.success_dialog_open = False
        self.change_username_dialog_open = False
        self.change_email_dialog_open = False
        self.change_password_dialog_open = False

    @rx.event
    def set_email_sent(self, email_sent: str):
        self.email_sent = email_sent

    @rx.event
    def reset_countdown(self):
        self.countdown = 0

    @rx.event
    def send_email(self): 
        if self.email_sent == "":
            self.base_dialog_description = "邮箱不能为空"
            return self.account_dialog_open_change()
        if not validate_email(email=self.email_sent):
            self.base_dialog_description = "邮箱格式错误"
            return self.account_dialog_open_change()
        if self.email_sent == self.email:
            self.base_dialog_description = "新邮箱不能和原邮箱相同"
            return self.account_dialog_open_change()
        with rx.session() as session:
            if session.exec(select(User).where(User.email == self.email_sent)).first():
                self.base_dialog_description = "邮箱已被使用"
                return self.account_dialog_open_change()
        self.send_time = datetime.datetime.now()
        self.captcha = send_email(msg_to=self.email_sent)
        print(self.captcha)
        self.base_dialog_description = "验证码发送成功!"
        self.account_dialog_open_change()
        return AccountState.count

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
    def change_username(self,form_data: dict):
        username = form_data.get('username','')
        if username == "":
            self.base_dialog_description = "用户名不能为空"
            return self.account_dialog_open_change()
        if " " in username:
            self.base_dialog_description = "用户名不能含有空格"
            return self.account_dialog_open_change()
        if username == self.username:
            self.base_dialog_description = "新用户名不能和原用户名相同"
            return self.account_dialog_open_change()
        if len(username) < 6 or len(username) > 10:
            self.base_dialog_description = "用户名长度应在6位到10位间"
            return self.account_dialog_open_change()
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.email == self.email)
            ).first()
            if session.exec(select(User).where(User.username == username)).first():
                self.base_dialog_description = "用户名已存在"
                return self.account_dialog_open_change()
            self.username = username
            user.username = username     
            session.add(user)
            session.commit()
            self.base_dialog_description = "修改用户名成功"
            return self.success_dialog_open_change()
        
    @rx.event
    def change_email(self,form_data: dict):
        email_form = form_data.get('email','')
        captcha = form_data.get('captcha','')
        if email_form == "":
            self.base_dialog_description = "邮箱不能为空"
            return self.account_dialog_open_change()
        if not validate_email(email=email_form):
            self.base_dialog_description = "邮箱格式错误"
            return self.account_dialog_open_change()
        if self.email == email_form:
            self.base_dialog_description = "新邮箱不能和原邮箱相同"
            return self.account_dialog_open_change()
        if self.email_sent != email_form or self.captcha != captcha:
            self.base_dialog_description = "验证码错误"
            return self.account_dialog_open_change()
        if (datetime.datetime.now() - self.send_time).total_seconds() > 300:
            self.base_dialog_description = "验证码已过期"
            return self.account_dialog_open_change()
        
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.username == self.username)
            ).first()
            self.email = email_form
            user.email = email_form  
            session.add(user)
            session.commit()
        self.reset_countdown()
        self.base_dialog_description = "修改邮箱成功"
        return self.success_dialog_open_change()

    @rx.event
    def change_password(self,form_data: dict):
        password = form_data.get('password','')
        confirm_password = form_data.get('confirm_password','')
        if password == "":
            self.base_dialog_description = "密码不能为空"
            return self.account_dialog_open_change()
        if " " in password:
            self.base_dialog_description = "密码不能含有空格"
            return self.account_dialog_open_change()
        if len(password) < 8 or len(password) > 15:
            self.base_dialog_description = "密码长度应在8位到15位间"
            return self.account_dialog_open_change()
        if password != confirm_password:
            self.base_dialog_description = "密码与确认密码需完全相同"
            return self.account_dialog_open_change()
        if bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8')):
            self.base_dialog_description = "新密码不能和原密码相同"
            return self.account_dialog_open_change()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        print(hashed_password)
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.username == self.username)
            ).first()
            self.password = hashed_password
            user.password = hashed_password
            session.add(user)
            session.commit()
        self.base_dialog_description = "修改密码成功"
        return self.success_dialog_open_change()
