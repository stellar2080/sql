import asyncio
import reflex as rx
from .base_st import BaseState
import numpy as np
import pandas as pd

# def init_manager(self):
# self._manager = Manager(
#     config={
#         'user_id': self.user_id,
#         'platform': self.platform,
#         'model': self.model,
#         'LLM_HOST': self.LLM_HOST,
#         'LLM_PORT': self.LLM_PORT,
#         'target_db_path': target_db_path,
#         'vectordb_client': 'http',
#         'vectordb_host': 'localhost',
#         'vectordb_port': '8000',
#         'MAX_ITERATIONS': self.MAX_ITERATIONS,
#         'DO_SAMPLE': self.DO_SAMPLE,
#         'TEMPERATURE': self.TEMPERATURE,
#         'TOP_K': self.TOP_K,
#         'TOP_P': self.TOP_P,
#         'MAX_TOKENS': self.MAX_TOKENS,
#         'N_RESULTS': self.N_RESULTS,
#         'E_HINT_THRESHOLD': self.E_HINT_THRESHOLD,
#         'E_COL_THRESHOLD': self.E_COL_THRESHOLD,
#         'E_VAL_THRESHOLD': self.E_VAL_THRESHOLD,
#         'E_COL_STRONG_THRESHOLD': self.E_COL_STRONG_THRESHOLD,
#         'E_VAL_STRONG_THRESHOLD': self.E_VAL_STRONG_THRESHOLD,
#         'F_HINT_THRESHOLD': self.F_HINT_THRESHOLD,
#         'F_COL_THRESHOLD': self.F_COL_THRESHOLD,
#         'F_LSH_THRESHOLD': self.F_LSH_THRESHOLD,
#         'F_VAL_THRESHOLD': self.F_VAL_THRESHOLD,
#         'F_COL_STRONG_THRESHOLD': self.F_COL_STRONG_THRESHOLD,
#         'F_VAL_STRONG_THRESHOLD': self.F_VAL_STRONG_THRESHOLD,
#         'G_HINT_THRESHOLD': self.G_HINT_THRESHOLD,
#     },
# )

class QA(rx.Base):

    question: str
    answer_text: str
    table_datas: pd.DataFrame
    last: bool

class ChatState(BaseState):

    current_chat: list[QA] = []
    question: str
    processing: bool = False

    async def process_question(self, form_data):
        question = form_data["question"]
        if not question or question == "":
            return

        model = self.AI_process_question
        async for value in model(question):
            yield value

    async def AI_process_question(self, question: str):
        qa = QA(
            question=question, 
            answer_text='', 
            table_datas=pd.DataFrame(),
            last=True
        )
        self.current_chat.append(qa)
        yield
        self.processing = True
        yield
        await asyncio.sleep(5)
        last_qa = self.current_chat[-1]
        messages = []
        messages.append({"role": "user", "content": last_qa.question})

        data = np.random.rand(20, 8)

        df = pd.DataFrame(data,columns=['Column1', 'Column2','Column3', 'Column4','Column5', 'Column6','Column7', 'Column8'])

        self.current_chat[-1].answer_text = "123111111111111111111111你好你好你好你好你好你好你你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好你好好你好你好你好你好"
        self.current_chat[-1].table_datas = df

        self.current_chat[-1].last=False
        self.processing = False
        