import asyncio
import reflex as rx
from .base_st import BaseState
import numpy as np
import pandas as pd
from client.manager.manager import Manager
from rxconfig import target_db_path
from client.utils.const import EXTRACTOR, FILTER, GENERATOR, REVISER, MANAGER

class QA(rx.Base):

    question: str
    answer_text: str
    table_datas: pd.DataFrame
    text_loading: bool
    table_loading: bool

class ChatState(BaseState):

    current_chat: list[QA] = []
    question: str
    processing: bool = False

    def init_manager(self):
        return Manager(
            config={
                'user_id': self.user_id,
                'platform': self.platform,
                'model': self.model,
                'api_key': self.api_key,
                'LLM_HOST': self.LLM_HOST,
                'LLM_PORT': self.LLM_PORT,
                'target_db_path': target_db_path,
                'vectordb_host': 'localhost',
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
            table_datas=pd.DataFrame(),
            text_loading=True,
            table_loading=True,
        )
        async with self:
            self.current_chat.append(qa)

            self.processing = True
  
        last_qa = self.current_chat[-1]

        async with self:
            self.current_chat[-1].answer_text += '智能体：'+FILTER+'正在执行...\n'
            self.current_chat[-1].answer_text += '智能体：'+FILTER+'正在执行...\n'
            self.current_chat[-1].text_loading=False
        await asyncio.sleep(5)
        message = {
            'sql': '123',
            'sql_result': {
                'cols': ['c1'],
                'rows': [(1,),(2,)]
            }
        }
        sql_result = message.get('sql_result')
        cols = sql_result.get('cols')
        rows = sql_result.get('rows')
        df = pd.DataFrame(
            data=rows,
            columns=cols
        )
        async with self:
            self.current_chat[-1].answer_text = message.get('sql')
            self.current_chat[-1].table_datas = df
            self.current_chat[-1].table_loading=False
            self.processing = False

        # async with self:
        #     self.current_chat[-1].answer_text += '正在初始化...\n'
        #     self.current_chat[-1].text_loading=False 
        # manager = self.init_manager()
        # async with self:
        #     self.current_chat[-1].answer_text += '初始化成功...\n'
        # async_func =  manager.chat
        # async for message in async_func(last_qa.question):
        #     if message.get('message_to') == EXTRACTOR:
        #         async with self:
        #             self.current_chat[-1].answer_text += '智能体：'+EXTRACTOR+'正在提取实体...\n'
        #     elif message.get('message_to') == FILTER:
        #         async with self:
        #             self.current_chat[-1].answer_text += '智能体：'+EXTRACTOR + '已提取来自问题，知识库和数据库的可能的实体：\n'
        #             self.current_chat[-1].answer_text += str(message.get('entity')) + '\n'
        #             self.current_chat[-1].answer_text += '智能体：'+FILTER+'正在选取数据库的表和列...\n'
        #     elif message.get('message_to') == GENERATOR:
        #         async with self:
        #             self.current_chat[-1].answer_text += '智能体：'+FILTER + '已选取数据库的表和列：\n'
        #             self.current_chat[-1].answer_text += str(message.get('schema')) + '\n'
        #             self.current_chat[-1].answer_text += '智能体：'+GENERATOR+'正在生成SQL...\n'
        #     elif message.get('message_to') == REVISER:
        #         async with self:
        #             self.current_chat[-1].answer_text += '智能体：'+GENERATOR + '已生成SQL：\n'
        #             self.current_chat[-1].answer_text += message.get('sql') + '\n'
        #             self.current_chat[-1].answer_text += '智能体：'+REVISER+'正在执行和修正SQL...\n'
        #     elif message.get('message_to') == MANAGER:
        #         sql_result = message.get('sql_result')
        #         cols = sql_result.get('cols')
        #         rows = sql_result.get('rows')
        #         df = pd.DataFrame(
        #             data=rows,
        #             columns=cols
        #         )
        #         async with self:
        #             self.current_chat[-1].table_datas = df
        #             self.current_chat[-1].table_loading=False
        #             self.processing = False
        