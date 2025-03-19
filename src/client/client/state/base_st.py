import typing
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
        self.base_dialog_description = "恢复默认设置成功，不要忘了保存设置"
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
    
    MAX_ITERATIONS: int = 3
    DO_SAMPLE: bool = False
    TEMPERATURE: float = 0.1
    TOP_K: int = 3
    TOP_P: float = 0.1
    MAX_TOKENS: int = 8192
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
            self.MAX_TOKENS = ai_config.MAX_TOKENS
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

    @rx.event
    def set_MAX_ITERATIONS(self, MAX_ITERATIONS: list[typing.Union[int, float]]):
        self.MAX_ITERATIONS = MAX_ITERATIONS[0]

    @rx.event
    def set_DO_SAMPLE(self, DO_SAMPLE: bool):
        self.DO_SAMPLE = DO_SAMPLE

    @rx.event
    def set_TEMPERATURE(self, TEMPERATURE: list[typing.Union[int, float]]):
        self.TEMPERATURE = TEMPERATURE[0]

    @rx.event
    def set_TOP_K(self, TOP_K: list[typing.Union[int, float]]):
        self.TOP_K = TOP_K[0]

    @rx.event
    def set_TOP_P(self, TOP_P: list[typing.Union[int, float]]):
        self.TOP_P = TOP_P[0]

    @rx.event
    def set_MAX_TOKENS(self, MAX_TOKENS: list[typing.Union[int, float]]):
        self.MAX_TOKENS = MAX_TOKENS[0]

    @rx.event
    def set_N_RESULTS(self, N_RESULTS: int):
        self.N_RESULTS = N_RESULTS

    @rx.event
    def set_E_HINT_THRESHOLD(self, E_HINT_THRESHOLD: float):
        self.E_HINT_THRESHOLD = E_HINT_THRESHOLD

    @rx.event
    def set_E_COL_THRESHOLD(self, E_COL_THRESHOLD: float):
        self.E_COL_THRESHOLD = E_COL_THRESHOLD

    @rx.event
    def set_E_VAL_THRESHOLD(self, E_VAL_THRESHOLD: float):
        self.E_VAL_THRESHOLD = E_VAL_THRESHOLD

    @rx.event
    def set_E_COL_STRONG_THRESHOLD(self, E_COL_STRONG_THRESHOLD: float):
        self.E_COL_STRONG_THRESHOLD = E_COL_STRONG_THRESHOLD

    @rx.event
    def set_E_VAL_STRONG_THRESHOLD(self, E_VAL_STRONG_THRESHOLD: float):
        self.E_VAL_STRONG_THRESHOLD = E_VAL_STRONG_THRESHOLD

    @rx.event
    def set_F_HINT_THRESHOLD(self, F_HINT_THRESHOLD: float):
        self.F_HINT_THRESHOLD = F_HINT_THRESHOLD

    @rx.event
    def set_F_LSH_THRESHOLD(self, F_LSH_THRESHOLD: float):
        self.F_LSH_THRESHOLD = F_LSH_THRESHOLD

    @rx.event
    def set_F_COL_THRESHOLD(self, F_COL_THRESHOLD: float):
        self.F_COL_THRESHOLD = F_COL_THRESHOLD

    @rx.event
    def set_F_VAL_THRESHOLD(self, F_VAL_THRESHOLD: float):
        self.F_VAL_THRESHOLD = F_VAL_THRESHOLD

    @rx.event
    def set_F_COL_STRONG_THRESHOLD(self, F_COL_STRONG_THRESHOLD: float):
        self.F_COL_STRONG_THRESHOLD = F_COL_STRONG_THRESHOLD

    @rx.event
    def set_F_VAL_STRONG_THRESHOLD(self, F_VAL_STRONG_THRESHOLD: float):
        self.F_VAL_STRONG_THRESHOLD = F_VAL_STRONG_THRESHOLD

    @rx.event
    def set_G_HINT_THRESHOLD(self, G_HINT_THRESHOLD: float):
        self.G_HINT_THRESHOLD = G_HINT_THRESHOLD

    @rx.event
    def set_LLM_HOST(self, LLM_HOST: str):
        self.LLM_HOST = LLM_HOST

    @rx.event
    def set_LLM_PORT(self, LLM_PORT: int):
        self.LLM_PORT = LLM_PORT