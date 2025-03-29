import bcrypt
import reflex as rx
from sqlmodel import select, or_
from client.db_model import User, Settings

class BaseState(rx.State):

    user_id: str = None
    username: str = None
    email: str = None
    password: str = None

    base_dialog_description: str = ""
    base_dialog_open: bool = False
    
    auth_success_dialog_open: bool = False

    @rx.event
    def base_dialog_open_change(self):
        self.base_dialog_open = not self.base_dialog_open

    @rx.event
    def auth_success_dialog_open_change(self):
        self.auth_success_dialog_open = not self.auth_success_dialog_open

    @rx.event
    def auth_success_redirect(self):
        self.auth_success_dialog_open_change()
        return rx.redirect("/chat")
    
    @rx.event
    def login(self, form_data: dict):
        user = form_data.get('user','')
        password = form_data.get('password','')
        if user == "" or password == "":
            self.base_dialog_description = "请填写所有信息"
            return self.base_dialog_open_change()
        if " " in user:
            self.base_dialog_description = "用户名不能含有空格"
            return self.base_dialog_open_change()
        if " " in password:
            self.base_dialog_description = "密码不能含有空格"
            return self.base_dialog_open_change()
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
                self.base_dialog_description = "用户名/邮箱错误"
                return self.base_dialog_open_change()
            elif not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                self.base_dialog_description = "密码错误"
                return self.base_dialog_open_change()
            else:
                self.user_id = user.user_id
                self.username = user.username
                self.email = user.email
                self.password = user.password
                self.base_dialog_description = "登录成功，欢迎回来，" + self.username
                self.load_settings()
                return self.auth_success_dialog_open_change()

    @rx.event
    def logout(self):
        self.reset()
        return rx.redirect("/login")
    
    @rx.var
    def logged_in(self) -> bool:
        return self.user_id is not None
            
    @rx.event
    def check_login(self):
        if not self.logged_in:
            return rx.redirect("/login")
        
    accent_color: str = "violet"
    gray_color: str = "gray"
    radius: str = "large"
    scaling: str = "100%"

    settings_reset_open: bool = False
    settings_saved_open: bool = False
    
    @rx.event
    def settings_reset_open_change(self):
        self.settings_reset_open = not self.settings_reset_open

    @rx.event
    def settings_saved_open_change(self):
        self.settings_saved_open = not self.settings_saved_open

    @rx.event()
    def load_settings(self):
        with rx.session() as session:
            settings = session.exec(
                Settings.select().where(
                    Settings.user_id == self.user_id,
                )
            ).first()
            self.accent_color = settings.accent_color
            self.gray_color = settings.gray_color
            self.radius = settings.radius
            self.scaling = settings.scaling
   
    @rx.event
    def set_accent_color(self, accent_color: str):
        self.accent_color = accent_color

    @rx.event
    def set_gray_color(self, gray_color: str):
        self.gray_color = gray_color

    @rx.event
    def set_radius(self, radius: str):
        self.radius = radius

    @rx.event
    def set_scaling(self, scaling: str):
        self.scaling = scaling

    @rx.event
    def reset_settings(self):
        self.accent_color = "violet"
        self.gray_color = "gray"
        self.radius = "large"
        self.scaling = "100%"
        self.base_dialog_description = "恢复默认设置成功，不要忘了保存设置"
        self.settings_reset_open_change()

    @rx.event
    def save_settings(self):
        with rx.session() as session:
            settings = session.exec(
                Settings.select().where(
                    Settings.user_id == self.user_id
                )
            ).first()
            settings.accent_color = self.accent_color
            settings.gray_color = self.gray_color
            settings.radius = self.radius
            settings.scaling = self.scaling
            session.add(settings)
            session.commit()
        self.base_dialog_description = "保存设置成功"
        return self.settings_saved_open_change()