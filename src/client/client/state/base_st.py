import bcrypt
import reflex as rx
from sqlmodel import select, or_
from client.db_model import User, Settings

class BaseState(rx.State):

    user_id: str = None
    username: str = None
    email: str = None
    password: str = None

    accent_color: str = "violet"
    gray_color: str = "gray"
    radius: str = "large"
    scaling: str = "100%"

    @rx.event
    def login(self, form_data: dict):
        user = form_data.get('user','')
        password = form_data.get('password','')
        if user == "" or password == "":
            return rx.toast.error("请填写所有信息", duration=2000, position='top-center')
        if " " in user:
            return rx.toast.error("用户名不能含有空格", duration=2000, position='top-center')
        if " " in password:
            return rx.toast.error("密码不能含有空格", duration=2000, position='top-center')
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
                return rx.toast.error("用户名/邮箱错误", duration=2000, position='top-center')
            elif not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return rx.toast.error("密码错误", duration=2000, position='top-center')
            else:
                self.user_id = user.user_id
                self.username = user.username
                self.email = user.email
                self.password = user.password
                self.load_settings()
                yield rx.toast.success("登录成功，欢迎回来，" + self.username, duration=2000, position='top-center')
                return rx.redirect("/chat")

    @rx.event
    def logout(self):
        self.reset()
        yield rx.toast.success('已退出登录', position='top-center')
        return rx.redirect("/login")
    
    @rx.var
    def logged_in(self) -> bool:
        return self.user_id is not None
            
    @rx.event
    def check_login(self):
        if not self.logged_in:
            return rx.redirect("/login")
        
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
        return rx.toast.success("恢复默认设置成功，不要忘了保存设置", duration=2000, position='top-center')

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
        return rx.toast.success("保存设置成功", duration=2000, position='top-center')