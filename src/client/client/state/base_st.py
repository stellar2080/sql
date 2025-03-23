import os
import bcrypt
import reflex as rx
from sqlmodel import select, or_
from client.db_model import User, Settings, AIConfig
from client.utils.utils import is_valid_ipv4, is_float

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
                self.load_settings()
                self.load_ai_config()
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
                select(Settings).where(
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
    
    platform: str = 'Tongyi'
    model: str = 'qwen-max'
    api_key: str = ''
    LLM_HOST: str = 'localhost'
    LLM_PORT: int = 6006
    MAX_ITERATIONS: int = 3
    DO_SAMPLE: bool = False
    TEMPERATURE: float = 0.1
    TOP_P: float = 0.1
    MAX_TOKENS: int = 8192
    N_RESULTS: int = 3
    E_HINT_THRESHOLD: float = 0.30
    E_COL_THRESHOLD: float = 0.30
    E_VAL_THRESHOLD: float = 0.30
    E_COL_STRONG_THRESHOLD: float = 0.48
    E_VAL_STRONG_THRESHOLD: float = 0.48
    F_HINT_THRESHOLD: float = 0.80
    F_COL_THRESHOLD: float = 0.60
    F_LSH_THRESHOLD: float = 0.40
    F_VAL_THRESHOLD: float = 0.60
    F_COL_STRONG_THRESHOLD: float = 0.85
    F_VAL_STRONG_THRESHOLD: float = 0.85
    G_HINT_THRESHOLD: float = 0.30

    @rx.var
    def get_MAX_ITERATIONS(self) -> str:
        return str(self.MAX_ITERATIONS)

    @rx.var
    def get_TEMPERATURE(self) -> str:
        return str(self.TEMPERATURE)

    @rx.var
    def get_TOP_P(self) -> str:
        return str(self.TOP_P)

    @rx.var
    def get_MAX_TOKENS(self) -> str:
        return str(self.MAX_TOKENS)

    @rx.var
    def get_N_RESULTS(self) -> str:
        return str(self.N_RESULTS)

    @rx.var
    def get_E_HINT_THRESHOLD(self) -> str:
        return str(self.E_HINT_THRESHOLD)

    @rx.var
    def get_E_COL_THRESHOLD(self) -> str:
        return str(self.E_COL_THRESHOLD)

    @rx.var
    def get_E_VAL_THRESHOLD(self) -> str:
        return str(self.E_VAL_THRESHOLD)

    @rx.var
    def get_E_COL_STRONG_THRESHOLD(self) -> str:
        return str(self.E_COL_STRONG_THRESHOLD)

    @rx.var
    def get_E_VAL_STRONG_THRESHOLD(self) -> str:
        return str(self.E_VAL_STRONG_THRESHOLD)

    @rx.var
    def get_F_HINT_THRESHOLD(self) -> str:
        return str(self.F_HINT_THRESHOLD)

    @rx.var
    def get_F_COL_THRESHOLD(self) -> str:
        return str(self.F_COL_THRESHOLD)

    @rx.var
    def get_F_LSH_THRESHOLD(self) -> str:
        return str(self.F_LSH_THRESHOLD)

    @rx.var
    def get_F_VAL_THRESHOLD(self) -> str:
        return str(self.F_VAL_THRESHOLD)

    @rx.var
    def get_F_COL_STRONG_THRESHOLD(self) -> str:
        return str(self.F_COL_STRONG_THRESHOLD)

    @rx.var
    def get_F_VAL_STRONG_THRESHOLD(self) -> str:
        return str(self.F_VAL_STRONG_THRESHOLD)

    @rx.var
    def get_G_HINT_THRESHOLD(self) -> str:
        return str(self.G_HINT_THRESHOLD)

    @rx.var
    def get_LLM_PORT(self) -> str:
        return str(self.LLM_PORT)

    @rx.event
    def load_ai_config(self):
        with rx.session() as session:
            ai_config = session.exec(
                select(AIConfig).where(
                    AIConfig.user_id == self.user_id,
                )
            ).first()
            self.platform = ai_config.platform
            self.model = ai_config.model
            self.api_key = ai_config.api_key
            self.LLM_HOST = ai_config.LLM_HOST
            self.LLM_PORT = ai_config.LLM_PORT
            self.MAX_ITERATIONS = ai_config.MAX_ITERATIONS
            self.DO_SAMPLE = ai_config.DO_SAMPLE
            self.TEMPERATURE = ai_config.TEMPERATURE
            self.TOP_P = ai_config.TOP_P
            self.MAX_TOKENS = ai_config.MAX_TOKENS
            self.N_RESULTS = ai_config.N_RESULTS
            self.E_HINT_THRESHOLD = ai_config.E_HINT_THRESHOLD
            self.E_COL_THRESHOLD = ai_config.E_COL_THRESHOLD
            self.E_VAL_THRESHOLD = ai_config.E_VAL_THRESHOLD
            self.E_COL_STRONG_THRESHOLD = ai_config.E_COL_STRONG_THRESHOLD
            self.E_VAL_STRONG_THRESHOLD = ai_config.E_VAL_STRONG_THRESHOLD
            self.F_HINT_THRESHOLD = ai_config.F_HINT_THRESHOLD
            self.F_COL_THRESHOLD = ai_config.F_COL_THRESHOLD
            self.F_LSH_THRESHOLD = ai_config.F_LSH_THRESHOLD
            self.F_VAL_THRESHOLD = ai_config.F_VAL_THRESHOLD
            self.F_COL_STRONG_THRESHOLD = ai_config.F_COL_STRONG_THRESHOLD
            self.F_VAL_STRONG_THRESHOLD = ai_config.F_VAL_STRONG_THRESHOLD
            self.G_HINT_THRESHOLD = ai_config.G_HINT_THRESHOLD


    @rx.event
    def save_ai_config(self, form_data: dict):
        platform = form_data.get('platform')
        model = form_data.get('model')
        api_key = form_data.get('api_key')
        LLM_HOST = form_data.get('LLM_HOST')
        LLM_PORT = form_data.get('LLM_PORT')

        if platform == 'Tongyi':
            api_key = form_data.get('api_key')
            if api_key == '':
                self.base_dialog_description = "请输入api_key"
                return self.base_dialog_open_change()
            
            if not (is_valid_ipv4(LLM_HOST) or LLM_HOST.lower() == 'localhost' or LLM_HOST == ''):
                self.base_dialog_description = "请输入正确的ip地址或将ip地址置空"
                return self.base_dialog_open_change()

            if LLM_PORT.isdigit():
                LLM_PORT = int(LLM_PORT)
                if LLM_PORT < 0 or LLM_PORT > 65535:
                    self.base_dialog_description = "端口号范围应为：[0, 65535]"
                    return self.base_dialog_open_change()
            elif LLM_PORT == '':
                LLM_PORT = -1
            else:
                self.base_dialog_description = "请输入正确的端口号或将端口号置空"
                return self.base_dialog_open_change()
            
        elif platform == 'Custom':
            if not (is_valid_ipv4(LLM_HOST) or LLM_HOST.lower() == 'localhost'):
                self.base_dialog_description = "请输入正确的ip地址"
                return self.base_dialog_open_change()
            
            if not LLM_PORT.isdigit():
                self.base_dialog_description = "请输入正确的端口号"
                return self.base_dialog_open_change()
            LLM_PORT = int(LLM_PORT)
            if LLM_PORT < 0 or LLM_PORT > 65535:
                self.base_dialog_description = "端口号范围应为：[0, 65535]"
                return self.base_dialog_open_change()

        MAX_ITERATIONS = form_data.get('MAX_ITERATIONS')
        if not MAX_ITERATIONS.isdigit():
            self.base_dialog_description = "最大修正轮次的取值应为整数"
            return self.base_dialog_open_change()
        MAX_ITERATIONS = int(MAX_ITERATIONS)
        if MAX_ITERATIONS < 0 or MAX_ITERATIONS > 10:
            self.base_dialog_description = "最大修正轮次的取值范围应为：[0, 10]"
            return self.base_dialog_open_change()

        DO_SAMPLE = True if form_data.get('DO_SAMPLE') == 'on' else False
    
        TEMPERATURE = form_data.get('TEMPERATURE')
        if not is_float(TEMPERATURE):
            self.base_dialog_description = "TEMPERATURE的取值应为小数"
            return self.base_dialog_open_change()
        TEMPERATURE = float(TEMPERATURE)
        if TEMPERATURE < 0 or TEMPERATURE >= 2.0:
            self.base_dialog_description = "TEMPERATURE的取值范围应为：[0, 2.0)"
            return self.base_dialog_open_change()
        
        TOP_P = form_data.get('TOP_P')
        if not is_float(TOP_P):
            self.base_dialog_description = "TOP_P的取值应为小数"
            return self.base_dialog_open_change()
        TOP_P = float(TOP_P)
        if TOP_P <= 0 or TOP_P > 1.0:
            self.base_dialog_description = "TOP_P的取值范围应为：(0,1.0]"
            return self.base_dialog_open_change()

        MAX_TOKENS = form_data.get('MAX_TOKENS')
        if not MAX_TOKENS.isdigit():
            self.base_dialog_description = "MAX_TOKENS的取值应为整数"
            return self.base_dialog_open_change()
        MAX_TOKENS = int(MAX_TOKENS)
        if MAX_TOKENS < 100 or MAX_TOKENS > 8192:
            self.base_dialog_description = "MAX_TOKENS的取值范围应为：[100,8192]"
            return self.base_dialog_open_change()
        
        N_RESULTS = form_data.get('N_RESULTS')
        if not N_RESULTS.isdigit():
            self.base_dialog_description = "N_RESULTS的取值应为整数"
            return self.base_dialog_open_change()
        N_RESULTS = int(N_RESULTS)
        if N_RESULTS < 1 or N_RESULTS > 10:
            self.base_dialog_description = "N_RESULTS的取值范围应为：[1,10]"
            return self.base_dialog_open_change()

        E_HINT_THRESHOLD = form_data.get('E_HINT_THRESHOLD')
        if not is_float(E_HINT_THRESHOLD):
            self.base_dialog_description = "E_HINT_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        E_HINT_THRESHOLD = float(E_HINT_THRESHOLD)
        if E_HINT_THRESHOLD <= 0 or E_HINT_THRESHOLD > 1.0:
            self.base_dialog_description = "E_HINT_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()

        E_COL_THRESHOLD = form_data.get('E_COL_THRESHOLD')
        if not is_float(E_COL_THRESHOLD):
            self.base_dialog_description = "E_COL_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        E_COL_THRESHOLD = float(E_COL_THRESHOLD)
        if E_COL_THRESHOLD <= 0 or E_COL_THRESHOLD > 1.0:
            self.base_dialog_description = "E_COL_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()

        E_VAL_THRESHOLD = form_data.get('E_VAL_THRESHOLD')
        if not is_float(E_VAL_THRESHOLD):
            self.base_dialog_description = "E_VAL_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        E_VAL_THRESHOLD = float(E_VAL_THRESHOLD)
        if E_VAL_THRESHOLD <= 0 or E_VAL_THRESHOLD > 1.0:
            self.base_dialog_description = "E_VAL_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()

        E_COL_STRONG_THRESHOLD = form_data.get('E_COL_STRONG_THRESHOLD')
        if not is_float(E_COL_STRONG_THRESHOLD):
            self.base_dialog_description = "E_COL_STRONG_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        E_COL_STRONG_THRESHOLD = float(E_COL_STRONG_THRESHOLD)
        if E_COL_STRONG_THRESHOLD <= 0 or E_COL_STRONG_THRESHOLD > 1.0:
            self.base_dialog_description = "E_COL_STRONG_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        E_VAL_STRONG_THRESHOLD = form_data.get('E_VAL_STRONG_THRESHOLD')
        if not is_float(E_VAL_STRONG_THRESHOLD):
            self.base_dialog_description = "E_VAL_STRONG_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        E_VAL_STRONG_THRESHOLD = float(E_VAL_STRONG_THRESHOLD)
        if E_VAL_STRONG_THRESHOLD <= 0 or E_VAL_STRONG_THRESHOLD > 1.0:
            self.base_dialog_description = "E_VAL_STRONG_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        F_HINT_THRESHOLD = form_data.get('F_HINT_THRESHOLD')
        if not is_float(F_HINT_THRESHOLD):
            self.base_dialog_description = "F_HINT_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        F_HINT_THRESHOLD = float(F_HINT_THRESHOLD)
        if F_HINT_THRESHOLD <= 0 or F_HINT_THRESHOLD > 1.0:
            self.base_dialog_description = "F_HINT_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        F_COL_THRESHOLD = form_data.get('F_COL_THRESHOLD')
        if not is_float(F_COL_THRESHOLD):
            self.base_dialog_description = "F_COL_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        F_COL_THRESHOLD = float(F_COL_THRESHOLD)
        if F_COL_THRESHOLD <= 0 or F_COL_THRESHOLD > 1.0:
            self.base_dialog_description = "F_COL_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        F_LSH_THRESHOLD = form_data.get('F_LSH_THRESHOLD')
        if not is_float(F_LSH_THRESHOLD):
            self.base_dialog_description = "F_LSH_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        F_LSH_THRESHOLD = float(F_LSH_THRESHOLD)
        if F_LSH_THRESHOLD <= 0 or F_LSH_THRESHOLD > 1.0:
            self.base_dialog_description = "F_LSH_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        F_VAL_THRESHOLD = form_data.get('F_VAL_THRESHOLD')
        if not is_float(F_VAL_THRESHOLD):
            self.base_dialog_description = "F_VAL_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        F_VAL_THRESHOLD = float(F_VAL_THRESHOLD)
        if F_VAL_THRESHOLD <= 0 or F_VAL_THRESHOLD > 1.0:
            self.base_dialog_description = "F_VAL_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        F_COL_STRONG_THRESHOLD = form_data.get('F_COL_STRONG_THRESHOLD')
        if not is_float(F_COL_STRONG_THRESHOLD):
            self.base_dialog_description = "F_COL_STRONG_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        F_COL_STRONG_THRESHOLD = float(F_COL_STRONG_THRESHOLD)
        if F_COL_STRONG_THRESHOLD <= 0 or F_COL_STRONG_THRESHOLD > 1.0:
            self.base_dialog_description = "F_COL_STRONG_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        F_VAL_STRONG_THRESHOLD = form_data.get('F_VAL_STRONG_THRESHOLD')
        if not is_float(F_VAL_STRONG_THRESHOLD):
            self.base_dialog_description = "F_VAL_STRONG_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        F_VAL_STRONG_THRESHOLD = float(F_VAL_STRONG_THRESHOLD)
        if F_VAL_STRONG_THRESHOLD <= 0 or F_VAL_STRONG_THRESHOLD > 1.0:
            self.base_dialog_description = "F_VAL_STRONG_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()
        
        G_HINT_THRESHOLD = form_data.get('G_HINT_THRESHOLD')
        if not is_float(G_HINT_THRESHOLD):
            self.base_dialog_description = "G_HINT_THRESHOLD的取值应为小数"
            return self.base_dialog_open_change()
        G_HINT_THRESHOLD = float(G_HINT_THRESHOLD)
        if G_HINT_THRESHOLD <= 0 or G_HINT_THRESHOLD > 1.0:
            self.base_dialog_description = "G_HINT_THRESHOLD的取值范围应为：(0,1.00]"
            return self.base_dialog_open_change()

        self.platform = platform
        self.model = model
        self.api_key = api_key
        self.LLM_HOST = LLM_HOST
        self.LLM_PORT = LLM_PORT
        self.MAX_ITERATIONS = MAX_ITERATIONS
        self.DO_SAMPLE = DO_SAMPLE
        self.TEMPERATURE = TEMPERATURE
        self.TOP_P = TOP_P
        self.MAX_TOKENS = MAX_TOKENS
        self.N_RESULTS = N_RESULTS
        self.E_HINT_THRESHOLD = E_HINT_THRESHOLD
        self.E_COL_THRESHOLD = E_COL_THRESHOLD
        self.E_VAL_THRESHOLD = E_VAL_THRESHOLD
        self.E_COL_STRONG_THRESHOLD = E_COL_STRONG_THRESHOLD
        self.E_VAL_STRONG_THRESHOLD = E_VAL_STRONG_THRESHOLD
        self.F_HINT_THRESHOLD = F_HINT_THRESHOLD
        self.F_COL_THRESHOLD = F_COL_THRESHOLD
        self.F_LSH_THRESHOLD = F_LSH_THRESHOLD
        self.F_VAL_THRESHOLD = F_VAL_THRESHOLD
        self.F_COL_STRONG_THRESHOLD = F_COL_STRONG_THRESHOLD
        self.F_VAL_STRONG_THRESHOLD = F_VAL_STRONG_THRESHOLD
        self.G_HINT_THRESHOLD = G_HINT_THRESHOLD

        with rx.session() as session:
            ai_config = session.exec(
                select(AIConfig).where(
                    AIConfig.user_id == self.user_id
                )
            ).first()
            ai_config.platform = platform
            ai_config.model = model
            ai_config.api_key = api_key
            ai_config.LLM_HOST = LLM_HOST
            ai_config.LLM_PORT = LLM_PORT
            ai_config.MAX_ITERATIONS = MAX_ITERATIONS
            ai_config.DO_SAMPLE = DO_SAMPLE
            ai_config.TEMPERATURE = TEMPERATURE
            ai_config.TOP_P = TOP_P
            ai_config.MAX_TOKENS = MAX_TOKENS
            ai_config.N_RESULTS = N_RESULTS
            ai_config.E_HINT_THRESHOLD = E_HINT_THRESHOLD
            ai_config.E_COL_THRESHOLD = E_COL_THRESHOLD
            ai_config.E_VAL_THRESHOLD = E_VAL_THRESHOLD
            ai_config.E_COL_STRONG_THRESHOLD = E_COL_STRONG_THRESHOLD
            ai_config.E_VAL_STRONG_THRESHOLD = E_VAL_STRONG_THRESHOLD
            ai_config.F_HINT_THRESHOLD = F_HINT_THRESHOLD
            ai_config.F_COL_THRESHOLD = F_COL_THRESHOLD
            ai_config.F_LSH_THRESHOLD = F_LSH_THRESHOLD
            ai_config.F_VAL_THRESHOLD = F_VAL_THRESHOLD
            ai_config.F_COL_STRONG_THRESHOLD = F_COL_STRONG_THRESHOLD
            ai_config.F_VAL_STRONG_THRESHOLD = F_VAL_STRONG_THRESHOLD
            ai_config.G_HINT_THRESHOLD = G_HINT_THRESHOLD
            session.add(ai_config)
            session.commit()
        self.base_dialog_description = "保存设置成功"
        return self.base_dialog_open_change()