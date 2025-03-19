import bcrypt
import reflex as rx
from sqlmodel import select, or_
from db_model import User, Settings, AIConfig

class BaseState(rx.State):

    user_id: str = None
    username: str = None
    email: str = None
    password: str = None

    base_dialog_description: str = ""
    base_dialog_open: bool = False
    auth_success_dialog_open: bool = False
    check_login_dialog_open: bool = False

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
    def check_login_dialog_open_change(self):
        self.check_login_dialog_open = not self.check_login_dialog_open

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
            self.base_dialog_description = "您还未登录，请先登录"
            self.check_login_dialog_open_change()
            return rx.redirect("/login")
        if not self.settings_loaded:
            self.settings_loaded = not self.settings_loaded
            return self.load_settings()
        if not self.ai_config_loaded:
            self.ai_config_loaded = not self.ai_config_loaded
            return self.load_ai_config()

    accent_color: str = "violet"
    gray_color: str = "gray"
    radius: str = "large"
    scaling: str = "100%"
    
    settings_loaded: bool = False

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
                select(Settings).where(
                    Settings.user_id == self.user_id,
                )
            ).first()
            self.accent_color = settings.accent_color
            self.gray_color = settings.gray_color
            self.radius = settings.radius
            self.scaling = settings.scaling

    @rx.event
    def reset_settings(self):
        self.accent_color = "violet"
        self.gray_color = "gray"
        self.radius = "large"
        self.scaling = "100%"
        self.base_dialog_description = "恢复默认设置成功，记得保存设置"
        self.settings_reset_open_change()
        
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
    def summit_settings(self):
        with rx.session() as session:
            settings = session.exec(
                select(Settings).where(
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
    
    MAX_ITERATIONS: int = 8
    DO_SAMPLE: bool = False
    TEMPERATURE: float = 0.1
    TOP_K: int = 3
    TOP_P: float = 0.1
    MAX_LENGTH: int = 8192
    N_RESULTS: int = 3
    E_HINT_THRESHOLD: float = 0.30
    E_COL_THRESHOLD: float = 0.30
    E_VAL_THRESHOLD: float = 0.30
    E_COL_STRONG_THRESHOLD: float = 0.48
    E_VAL_STRONG_THRESHOLD: float = 0.48
    F_HINT_THRESHOLD: float = 0.80
    F_LSH_THRESHOLD: float = 0.40
    F_COL_THRESHOLD: float = 0.60
    F_VAL_THRESHOLD: float = 0.60
    F_COL_STRONG_THRESHOLD: float = 0.85
    F_VAL_STRONG_THRESHOLD: float = 0.85
    G_HINT_THRESHOLD: float = 0.30
    LLM_HOST: str = 'localhost'
    LLM_PORT: int = 6006

    ai_config_loaded: bool = False

    ai_config_reset_open: bool = False
    ai_config_saved_open: bool = False
    
    @rx.event
    def ai_config_reset_open_change(self):
        self.ai_config_reset_open = not self.ai_config_reset_open

    @rx.event
    def ai_config_saved_open_change(self):
        self.ai_config_saved_open = not self.ai_config_saved_open

    @rx.event
    def reset_ai_config(self):
        self.MAX_ITERATIONS = 8
        self.DO_SAMPLE = False
        self.TEMPERATURE = 0.1
        self.TOP_K = 3
        self.TOP_P = 0.1
        self.MAX_LENGTH = 8192
        self.N_RESULTS = 3
        self.E_HINT_THRESHOLD = 0.30
        self.E_COL_THRESHOLD = 0.30
        self.E_VAL_THRESHOLD = 0.30
        self.E_COL_STRONG_THRESHOLD = 0.48
        self.E_VAL_STRONG_THRESHOLD = 0.48
        self.F_HINT_THRESHOLD = 0.80
        self.F_LSH_THRESHOLD = 0.40
        self.F_COL_THRESHOLD = 0.60
        self.F_VAL_THRESHOLD = 0.60
        self.F_COL_STRONG_THRESHOLD = 0.85
        self.F_VAL_STRONG_THRESHOLD = 0.85
        self.G_HINT_THRESHOLD = 0.30
        self.LLM_HOST = 'localhost'
        self.LLM_PORT = 6006

    @rx.event()
    def load_ai_config(self):
        with rx.session() as session:
            ai_config = session.exec(
                select(AIConfig).where(
                    AIConfig.user_id == self.user_id,
                )
            ).first()
            self.MAX_ITERATIONS = ai_config.MAX_ITERATIONS
            self.DO_SAMPLE = ai_config.DO_SAMPLE
            self.TEMPERATURE = ai_config.TEMPERATURE
            self.TOP_K = ai_config.TOP_K
            self.TOP_P = ai_config.TOP_P
            self.MAX_LENGTH = ai_config.MAX_LENGTH
            self.N_RESULTS = ai_config.N_RESULTS
            self.E_HINT_THRESHOLD = ai_config.E_HINT_THRESHOLD
            self.E_COL_THRESHOLD = ai_config.E_COL_THRESHOLD
            self.E_VAL_THRESHOLD = ai_config.E_VAL_THRESHOLD
            self.E_COL_STRONG_THRESHOLD = ai_config.E_COL_STRONG_THRESHOLD
            self.E_VAL_STRONG_THRESHOLD = ai_config.E_VAL_STRONG_THRESHOLD
            self.F_HINT_THRESHOLD = ai_config.F_HINT_THRESHOLD
            self.F_LSH_THRESHOLD = ai_config.F_LSH_THRESHOLD
            self.F_COL_THRESHOLD = ai_config.F_COL_THRESHOLD
            self.F_VAL_THRESHOLD = ai_config.F_VAL_THRESHOLD
            self.F_COL_STRONG_THRESHOLD = ai_config.F_COL_STRONG_THRESHOLD
            self.F_VAL_STRONG_THRESHOLD = ai_config.F_VAL_STRONG_THRESHOLD
            self.G_HINT_THRESHOLD = ai_config.G_HINT_THRESHOLD
            self.LLM_HOST = ai_config.LLM_HOST
            self.LLM_PORT = ai_config.LLM_PORT