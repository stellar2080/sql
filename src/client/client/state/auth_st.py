import bcrypt
import reflex as rx
from sqlmodel import select, or_
from db_model import User

class AuthState(rx.State):

    username: str = None
    email: str = None
    password: str = None

    auth_dialog_description: str = ""
    auth_dialog_open: bool = False
    authsuccess_dialog_open: bool = False

    check_auth_dialog_open: bool = False

    @rx.event
    def auth_dialog_open_change(self):
        self.auth_dialog_open = not self.auth_dialog_open

    @rx.event
    def authsuccess_dialog_open_change(self):
        self.authsuccess_dialog_open = not self.authsuccess_dialog_open

    @rx.event
    def auth_success_redirect(self):
        self.authsuccess_dialog_open_change()
        return rx.redirect("/account")
    
    @rx.event
    def check_auth_dialog_open_change(self):
        self.check_auth_dialog_open = not self.check_auth_dialog_open

    @rx.event
    def login(self, form_data: dict):
        user = form_data.get('user','')
        password = form_data.get('password','')
        if user == "" or password == "":
            self.auth_dialog_description = "请填写所有信息"
            return self.auth_dialog_open_change()
        if " " in user:
            self.auth_dialog_description = "用户名不能含有空格"
            return self.auth_dialog_open_change()
        if " " in password:
            self.auth_dialog_description = "密码不能含有空格"
            return self.auth_dialog_open_change()
        with rx.session() as session:
            user = session.exec(
                select(User).where(
                    or_(
                        User.username == user,
                        User.email == user
                    )
                )
            ).first()   
            if not user:
                self.auth_dialog_description = "用户名/邮箱错误"
                return self.auth_dialog_open_change()
            elif not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                self.auth_dialog_description = "密码错误"
                return self.auth_dialog_open_change()
            else:
                self.username = user.username
                self.email = user.email
                self.password = user.password
                self.auth_dialog_description = "登录成功，欢迎回来，" + self.username
                return self.authsuccess_dialog_open_change()

    @rx.event
    def logout(self):
        self.reset()
        return rx.redirect("/login")

    @rx.event
    def check_login(self):
        if not self.logged_in:
            self.auth_dialog_description = "您还未登录，请先登录"
            self.check_auth_dialog_open_change()
            return rx.redirect("/login")

    @rx.var
    def logged_in(self) -> bool:
        return self.username is not None