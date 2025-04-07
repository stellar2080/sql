import asyncio
import reflex as rx

from client.utils.utils import is_valid_ipv4, is_float, is_valid_sqlite_url
from .base_st import BaseState
from client.manager.manager import Manager
from client.utils.const import EXTRACTOR, FILTER, GENERATOR, REVISER, MANAGER
from client.db_model import AIConfig, ChatRecord
from datetime import datetime

class QA(rx.Base):

    question: str
    answer_text: str
    table_cols: list
    table_datas: list
    show_text: bool
    show_table: bool

class ChatState(BaseState):

    current_chat: list[QA] = []
    question: str
    processing: bool = False
    
    platform: str = 'Tongyi'
    model: str = 'qwen-max'
    api_key: str = ''
    LLM_HOST: str = '127.0.0.1'
    LLM_PORT: int = 6006
    target_db_url: str = ''
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

    config_loaded: bool = False

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
    
    @rx.var
    def get_target_db_url(self) -> str:
        return str(self.target_db_url)

    @rx.event
    def copy_answer_text(self, qa: QA):
        yield rx.toast.success('成功复制文本到剪贴板', duration=2000, position='top-center')
        return rx.set_clipboard(qa.answer_text)
    
    @rx.event
    def copy_table(self, qa: QA):
        yield rx.toast.success('成功复制表到剪贴板', duration=2000, position='top-center')
        return rx.set_clipboard(str({'cols':qa.table_cols,'data':qa.table_datas}))

    @rx.var
    def chat_empty(self) -> bool:
        return len(self.current_chat) == 0

    @rx.event
    def clear_chat(self):
        self.current_chat.clear()
        return rx.toast.success("清空对话成功", duration=2000, position='top-center')

    @rx.event
    def on_load(self):
        if not self.logged_in:
            return rx.redirect("/login")
        if not self.config_loaded:
            self.config_loaded = not self.config_loaded
            with rx.session() as session:
                ai_config = session.exec(
                    AIConfig.select().where(
                        AIConfig.user_id == self.user_id,
                    )
                ).first()
                self.platform = ai_config.platform
                self.model = ai_config.model
                self.api_key = ai_config.api_key
                self.LLM_HOST = ai_config.LLM_HOST
                self.LLM_PORT = ai_config.LLM_PORT
                self.target_db_url = ai_config.target_db_url
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
                return rx.toast.error("请输入api_key", duration=2000, position='top-center')
            
            if not (is_valid_ipv4(LLM_HOST) or LLM_HOST.lower() == 'localhost' or LLM_HOST == ''):
                return rx.toast.error("请输入正确的ip地址或将ip地址置空", duration=2000, position='top-center')

            if LLM_PORT.isdigit():
                LLM_PORT = int(LLM_PORT)
                if LLM_PORT < 0 or LLM_PORT > 65535:
                    return rx.toast.error("端口号范围应为：[0, 65535]", duration=2000, position='top-center')
            elif LLM_PORT == '':
                LLM_PORT = -1
            else:
                return rx.toast.error("请输入正确的端口号或将端口号置空", duration=2000, position='top-center')
            
        elif platform == 'Custom':
            if not (is_valid_ipv4(LLM_HOST) or LLM_HOST.lower() == 'localhost'):
                return rx.toast.error("请输入正确的ip地址", duration=2000, position='top-center')
            
            if not LLM_PORT.isdigit():
                return rx.toast.error("请输入正确的端口号", duration=2000, position='top-center')
            LLM_PORT = int(LLM_PORT)
            if LLM_PORT < 0 or LLM_PORT > 65535:
                return rx.toast.error("端口号范围应为：[0, 65535]", duration=2000, position='top-center')

        target_db_url = form_data.get('target_db_url')

        MAX_ITERATIONS = form_data.get('MAX_ITERATIONS')
        if not MAX_ITERATIONS.isdigit():
            return rx.toast.error("最大修正轮次的取值应为整数", duration=2000, position='top-center')
        MAX_ITERATIONS = int(MAX_ITERATIONS)
        if MAX_ITERATIONS < 0 or MAX_ITERATIONS > 10:
            return rx.toast.error("最大修正轮次的取值范围应为：[0, 10]", duration=2000, position='top-center')

        DO_SAMPLE = True if form_data.get('DO_SAMPLE') == 'on' else False
    
        TEMPERATURE = form_data.get('TEMPERATURE')
        if not is_float(TEMPERATURE):
            return rx.toast.error("TEMPERATURE的取值应为小数", duration=2000, position='top-center')
        TEMPERATURE = float(TEMPERATURE)
        if TEMPERATURE < 0 or TEMPERATURE >= 2.0:
            return rx.toast.error("TEMPERATURE的取值范围应为：[0, 2.0)", duration=2000, position='top-center')
        
        TOP_P = form_data.get('TOP_P')
        if not is_float(TOP_P):
            return rx.toast.error("TOP_P的取值应为小数", duration=2000, position='top-center')
        TOP_P = float(TOP_P)
        if TOP_P <= 0 or TOP_P > 1.0:
            return rx.toast.error("TOP_P的取值范围应为：(0,1.0]", duration=2000, position='top-center')

        MAX_TOKENS = form_data.get('MAX_TOKENS')
        if not MAX_TOKENS.isdigit():
            return rx.toast.error("MAX_TOKENS的取值应为整数", duration=2000, position='top-center')
        MAX_TOKENS = int(MAX_TOKENS)
        if MAX_TOKENS < 100 or MAX_TOKENS > 8192:
            return rx.toast.error("MAX_TOKENS的取值范围应为：[100,8192]", duration=2000, position='top-center')
        
        N_RESULTS = form_data.get('N_RESULTS')
        if not N_RESULTS.isdigit():
            return rx.toast.error("N_RESULTS的取值应为整数", duration=2000, position='top-center')
        N_RESULTS = int(N_RESULTS)
        if N_RESULTS < 1 or N_RESULTS > 10:
            return rx.toast.error("N_RESULTS的取值范围应为：[1,10]", duration=2000, position='top-center')

        E_HINT_THRESHOLD = form_data.get('E_HINT_THRESHOLD')
        if not is_float(E_HINT_THRESHOLD):
            return rx.toast.error("E_HINT_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        E_HINT_THRESHOLD = float(E_HINT_THRESHOLD)
        if E_HINT_THRESHOLD <= 0 or E_HINT_THRESHOLD > 1.0:
            return rx.toast.error("E_HINT_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')

        E_COL_THRESHOLD = form_data.get('E_COL_THRESHOLD')
        if not is_float(E_COL_THRESHOLD):
            return rx.toast.error("E_COL_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        E_COL_THRESHOLD = float(E_COL_THRESHOLD)
        if E_COL_THRESHOLD <= 0 or E_COL_THRESHOLD > 1.0:
            return rx.toast.error("E_COL_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')

        E_VAL_THRESHOLD = form_data.get('E_VAL_THRESHOLD')
        if not is_float(E_VAL_THRESHOLD):
            return rx.toast.error("E_VAL_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        E_VAL_THRESHOLD = float(E_VAL_THRESHOLD)
        if E_VAL_THRESHOLD <= 0 or E_VAL_THRESHOLD > 1.0:
            return rx.toast.error("E_VAL_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')

        E_COL_STRONG_THRESHOLD = form_data.get('E_COL_STRONG_THRESHOLD')
        if not is_float(E_COL_STRONG_THRESHOLD):
            return rx.toast.error("E_COL_STRONG_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        E_COL_STRONG_THRESHOLD = float(E_COL_STRONG_THRESHOLD)
        if E_COL_STRONG_THRESHOLD <= 0 or E_COL_STRONG_THRESHOLD > 1.0:
            return rx.toast.error("E_COL_STRONG_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        E_VAL_STRONG_THRESHOLD = form_data.get('E_VAL_STRONG_THRESHOLD')
        if not is_float(E_VAL_STRONG_THRESHOLD):
            return rx.toast.error("E_VAL_STRONG_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        E_VAL_STRONG_THRESHOLD = float(E_VAL_STRONG_THRESHOLD)
        if E_VAL_STRONG_THRESHOLD <= 0 or E_VAL_STRONG_THRESHOLD > 1.0:
            return rx.toast.error("E_VAL_STRONG_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        F_HINT_THRESHOLD = form_data.get('F_HINT_THRESHOLD')
        if not is_float(F_HINT_THRESHOLD):
            return rx.toast.error("F_HINT_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        F_HINT_THRESHOLD = float(F_HINT_THRESHOLD)
        if F_HINT_THRESHOLD <= 0 or F_HINT_THRESHOLD > 1.0:
            return rx.toast.error("F_HINT_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        F_COL_THRESHOLD = form_data.get('F_COL_THRESHOLD')
        if not is_float(F_COL_THRESHOLD):
            return rx.toast.error("F_COL_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        F_COL_THRESHOLD = float(F_COL_THRESHOLD)
        if F_COL_THRESHOLD <= 0 or F_COL_THRESHOLD > 1.0:
            return rx.toast.error("F_COL_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        F_LSH_THRESHOLD = form_data.get('F_LSH_THRESHOLD')
        if not is_float(F_LSH_THRESHOLD):
            return rx.toast.error("F_LSH_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        F_LSH_THRESHOLD = float(F_LSH_THRESHOLD)
        if F_LSH_THRESHOLD <= 0 or F_LSH_THRESHOLD > 1.0:
            return rx.toast.error("F_LSH_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        F_VAL_THRESHOLD = form_data.get('F_VAL_THRESHOLD')
        if not is_float(F_VAL_THRESHOLD):
            return rx.toast.error("F_VAL_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        F_VAL_THRESHOLD = float(F_VAL_THRESHOLD)
        if F_VAL_THRESHOLD <= 0 or F_VAL_THRESHOLD > 1.0:
            return rx.toast.error("F_VAL_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        F_COL_STRONG_THRESHOLD = form_data.get('F_COL_STRONG_THRESHOLD')
        if not is_float(F_COL_STRONG_THRESHOLD):
            return rx.toast.error("F_COL_STRONG_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        F_COL_STRONG_THRESHOLD = float(F_COL_STRONG_THRESHOLD)
        if F_COL_STRONG_THRESHOLD <= 0 or F_COL_STRONG_THRESHOLD > 1.0:
            return rx.toast.error("F_COL_STRONG_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        F_VAL_STRONG_THRESHOLD = form_data.get('F_VAL_STRONG_THRESHOLD')
        if not is_float(F_VAL_STRONG_THRESHOLD):
            return rx.toast.error("F_VAL_STRONG_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        F_VAL_STRONG_THRESHOLD = float(F_VAL_STRONG_THRESHOLD)
        if F_VAL_STRONG_THRESHOLD <= 0 or F_VAL_STRONG_THRESHOLD > 1.0:
            return rx.toast.error("F_VAL_STRONG_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')
        
        G_HINT_THRESHOLD = form_data.get('G_HINT_THRESHOLD')
        if not is_float(G_HINT_THRESHOLD):
            return rx.toast.error("G_HINT_THRESHOLD的取值应为小数", duration=2000, position='top-center')
        G_HINT_THRESHOLD = float(G_HINT_THRESHOLD)
        if G_HINT_THRESHOLD <= 0 or G_HINT_THRESHOLD > 1.0:
            return rx.toast.error("G_HINT_THRESHOLD的取值范围应为：(0,1.00]", duration=2000, position='top-center')

        self.platform = platform
        self.model = model
        self.api_key = api_key
        self.LLM_HOST = LLM_HOST
        self.LLM_PORT = LLM_PORT
        self.target_db_url = target_db_url
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
                AIConfig.select().where(
                    AIConfig.user_id == self.user_id
                )
            ).first()
            ai_config.platform = platform
            ai_config.model = model
            ai_config.api_key = api_key
            ai_config.LLM_HOST = LLM_HOST
            ai_config.LLM_PORT = LLM_PORT
            ai_config.target_db_url = target_db_url
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
        return rx.toast.success("保存设置成功", duration=2000)

    def init_manager(self):
        return Manager(
            config={
                'user_id': self.user_id,
                'platform': self.platform,
                'model': self.model,
                'api_key': self.api_key,
                'LLM_HOST': self.LLM_HOST,
                'LLM_PORT': self.LLM_PORT,
                'target_db_url': self.target_db_url,
                'vectordb_host': '127.0.0.1',
                'vectordb_port': '8000',
                'MAX_ITERATIONS': self.MAX_ITERATIONS,
                'DO_SAMPLE': self.DO_SAMPLE,
                'TEMPERATURE': self.TEMPERATURE,
                'TOP_P': self.TOP_P,
                'MAX_TOKENS': self.MAX_TOKENS,
                'N_RESULTS': self.N_RESULTS,
                'E_HINT_THRESHOLD': self.E_HINT_THRESHOLD,
                'E_COL_THRESHOLD': self.E_COL_THRESHOLD,
                'E_VAL_THRESHOLD': self.E_VAL_THRESHOLD,
                'E_COL_STRONG_THRESHOLD': self.E_COL_STRONG_THRESHOLD,
                'E_VAL_STRONG_THRESHOLD': self.E_VAL_STRONG_THRESHOLD,
                'F_HINT_THRESHOLD': self.F_HINT_THRESHOLD,
                'F_COL_THRESHOLD': self.F_COL_THRESHOLD,
                'F_LSH_THRESHOLD': self.F_LSH_THRESHOLD,
                'F_VAL_THRESHOLD': self.F_VAL_THRESHOLD,
                'F_COL_STRONG_THRESHOLD': self.F_COL_STRONG_THRESHOLD,
                'F_VAL_STRONG_THRESHOLD': self.F_VAL_STRONG_THRESHOLD,
                'G_HINT_THRESHOLD': self.G_HINT_THRESHOLD,
            },
        )

    @rx.event(background=True)
    async def AI_process_question(self, form_data):
        question = form_data["question"]
        if not question or question == "":
            return
        
        qa = QA(
            question=question, 
            answer_text='', 
            table_cols=[],
            table_datas=[],
            show_text=False,
            show_table=False,
        )
        async with self:
            self.current_chat.append(qa)

            self.processing = True
  
        last_qa = self.current_chat[-1]
        yield rx.scroll_to("bottom")

        # async with self:
        #     self.current_chat[-1].answer_text += '智能体：'+FILTER+'正在执行...\n'
        #     self.current_chat[-1].answer_text += '智能体：'+GENERATOR+'正在执行...\n'
        #     self.current_chat[-1].show_text=True
        # await asyncio.sleep(1)
        # message = {
        #     'sql': 'SELECT * \nFROM STUDENT',
        #     'sql_result': {
        #         'cols': ['c1','c2','c3','c4','c5','c6','c7'],
        #         'rows': [
        #             (1, 'GOON', 15.2, True, '2023-05-01', 'New York', 1024),
        #             (2, 'Banana', 8.7, False, '2023-05-02', 'Los Angeles', 768),
        #             (3, 'Orange', 12.1, True, '2023-05-03', 'Chicago', 1536),
        #             (4, 'Grape', 5.5, False, '2023-05-04', 'Houston', 512),
        #             (5, 'Mango', 9.9, True, '2023-05-05', 'Phoenix', 2048),
        #             (6, 'Pineapple', 7.3, False, '2023-05-06', 'Philadelphia', 896),
        #             (7, 'Peach', 6.8, True, '2023-05-07', 'San Antonio', 1280),
        #             (8, 'Pear', 4.2, False, '2023-05-08', 'San Diego', 640),
        #             (9, 'Cherry', 11.5, True, '2023-05-09', 'Dallas', 1792),
        #             (10, 'Berry', 3.9, False, '2023-05-10', 'San Jose', 256),
        #             (11, 'Watermelon', 10.4, True, '2023-05-11', 'Austin', 1152),
        #             (12, 'Kiwi', 5.1, False, '2023-05-12', 'Jacksonville', 384),
        #             (13, 'Lemon', 2.8, True, '2023-05-13', 'Fort Worth', 512),
        #             (14, 'Lime', 3.5, False, '2023-05-14', 'Columbus', 768),
        #             (15, 'Plum', 6.2, True, '2023-05-15', 'Charlotte', 1024),
        #             (16, 'Apricot', 4.9, False, '2023-05-16', 'San Francisco', 640),
        #             (17, 'Fig', 7.7, True, '2023-05-17', 'Indianapolis', 896),
        #             (18, 'Melon', 8.5, False, '2023-05-18', 'Seattle', 1280),
        #             (19, 'Papaya', 9.1, True, '2023-05-19', 'Denver', 1536),
        #             (20, 'Avocado', 12.8, False, '2023-05-20', 'Washington', 2048),
        #             (21, 'Coconut', 11.2, True, '2023-05-21', 'Boston', 1792),
        #             (22, 'Guava', 5.7, False, '2023-05-22', 'El Paso', 384),
        #             (23, 'Lychee', 8.3, True, '2023-05-23', 'Detroit', 1024),
        #             (24, 'Dragonfruit', 14.5, False, '2023-05-24', 'Nashville', 512),
        #             (25, 'Starfruit', 6.9, True, '2023-05-25', 'Portland', 1280),
        #             (26, 'Pomegranate', 10.1, False, '2023-05-26', 'Memphis', 768),
        #             (27, 'Blackberry', 4.7, True, '2023-05-27', 'Oklahoma City', 896),
        #             (28, 'Raspberry', 5.3, False, '2023-05-28', 'Las Vegas', 640),
        #             (29, 'Blueberry', 7.1, True, '2023-05-29', 'Louisville', 1536),
        #             (30, 'Cantaloupe', 9.5, False, '2023-05-30', 'Baltimore', 2048)
        #         ]
        #     }
        # }
        # sql = message.get('sql')
        # sql_result = message.get('sql_result')
        # cols = sql_result.get('cols')
        # rows = sql_result.get('rows')
        # async with self:
        #     self.current_chat[-1].answer_text += message.get('sql')
        #     self.current_chat[-1].table_cols = cols
        #     self.current_chat[-1].table_datas = rows
        #     self.current_chat[-1].show_table=True
        #     self.processing = False
        # chat_record = ChatRecord(
        #     user_id=self.user_id,
        #     question=question,
        #     sql=sql,
        #     sql_result=sql_result,
        #     create_time=datetime.now()
        # )
        # with rx.session() as session:
        #     session.add(chat_record)
        #     session.commit()

        async with self:
            self.current_chat[-1].answer_text += '--- 正在初始化...\n'
            self.current_chat[-1].show_text=True 
        manager = self.init_manager()
        async with self:
            self.current_chat[-1].answer_text += '--- 初始化成功...\n'
        async_func =  manager.chat
        async for message in async_func(last_qa.question):
            if message.get('message_to') == EXTRACTOR:
                async with self:
                    self.current_chat[-1].answer_text += '--- 智能体：'+EXTRACTOR+'正在提取实体...\n'
            elif message.get('message_to') == FILTER:
                async with self:
                    self.current_chat[-1].answer_text += '--- 智能体：'+EXTRACTOR + '已提取来自问题，知识库和数据库的可能的实体：\n'
                    self.current_chat[-1].answer_text += str(message.get('entity')) + '\n'
                    self.current_chat[-1].answer_text += '--- 智能体：'+FILTER+'正在选取数据库的表和列...\n'
            elif message.get('message_to') == GENERATOR:
                async with self:
                    self.current_chat[-1].answer_text += '--- 智能体：'+FILTER + '已选取数据库的表和列：\n'
                    self.current_chat[-1].answer_text += str(message.get('schema')) + '\n'
                    self.current_chat[-1].answer_text += '--- 智能体：'+GENERATOR+'正在生成SQL...\n'
            elif message.get('message_to') == REVISER:
                async with self:
                    self.current_chat[-1].answer_text += '--- 智能体：'+GENERATOR + '已生成SQL：\n'
                    self.current_chat[-1].answer_text += message.get('sql') + '\n'
                    self.current_chat[-1].answer_text += '--- 智能体：'+REVISER+'正在执行和修正SQL...\n'
            elif message.get('message_to') == MANAGER:
                sql = message.get('sql')
                sql_result = message.get('sql_result')
                cols = sql_result.get('cols')
                rows = sql_result.get('rows')
                async with self:
                    self.current_chat[-1].table_cols = cols
                    self.current_chat[-1].table_datas = rows
                    self.current_chat[-1].show_table=True
                    self.processing = False
                chat_record = ChatRecord(
                    user_id=self.user_id,
                    question=question,
                    sql=sql,
                    sql_result=sql_result,
                    create_time=datetime.now()
                )
                with rx.session() as session:
                    session.add(chat_record)
                    session.commit()