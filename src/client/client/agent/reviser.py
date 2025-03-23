import aiosqlite
from typing_extensions import override

from client.llm.llm_base import LLM_Base
from client.utils.const import REVISER, MANAGER
from client.utils.template import reviser_template_p1, reviser_template_p2, reviser_hint_template
from client.utils.utils import parse_sql, user_message, get_response_content, timeout
from client.agent.agent_base import Agent_Base


class Reviser(Agent_Base):
    def __init__(
        self,
        config
    ):
        super().__init__()
        self.platform = config['platform']
        self.target_db_path = config.get("target_db_path")

    async def run_sql(
        self,
        sql: str,
    ) -> dict:
        async with aiosqlite.connect(self.target_db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(sql)
            rows = await cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            result = {}
            result['cols'] = col_names
            result['rows'] = rows
        
        return result

    def create_reviser_prompt(
        self,
        message: dict,
        sqlite_error: str
    ) -> str:  
        dialect = message['dialect']
        schema_str = message['schema']
        hint_str = message['hint']
        question = message['question']
        sql = message['sql']
        if hint_str == "":
            prompt = reviser_template_p1.format(dialect, schema_str, question) + \
                reviser_template_p2.format(sql, sqlite_error)
        else:
            prompt = reviser_template_p1.format(dialect, schema_str, question) + \
                reviser_hint_template.format(hint_str) + \
                reviser_template_p2.format(sql, sqlite_error)
        print("="*10,"PROMPT","="*10)
        print(prompt)
        return prompt

    @timeout(90)
    async def revise(
        self,
        prompt: str,
        llm: LLM_Base,
    ):
        llm_message = [user_message(prompt)]
        response = await llm.call(llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        print("="*10,"ANSWER","="*10)
        print(answer)
        new_sql = parse_sql(text=answer)
        return new_sql

    @override
    async def chat(
        self,
        message: dict,
        llm: LLM_Base=None,
    ):
        if message["message_to"] != REVISER:
            raise Exception("The message should not be processed by " + REVISER +
                             ". It is sent to " + message["message_to"])
        else:
            # print("The message is being processed by " + REVISER + "...")
            error_str = ""
            except_flag = False
            sql_result = None
            try:
                sql_result = await self.run_sql(message["sql"])
            except Exception as error:
                error_str = str(error.args[0])
                except_flag = True

            if except_flag is False:
                message["message_to"] = MANAGER
                message["sql_result"] = sql_result
                return message
            else:
                prompt = self.create_reviser_prompt(message,error_str)
                new_sql = await self.revise(prompt, llm)
                message["sql"] = new_sql
                return message