import pandas as pd
from typing_extensions import override

from src.llm.llm_base import LLM_Base
from src.utils.const import REVISER, MANAGER, QUERY_MODE
from src.utils.template import reviser_template_p1, reviser_template_p2, reviser_hint_template
from src.utils.utils import parse_sql, user_message, get_response_content, timeout
from src.agent.agent_base import Agent_Base


class Reviser(Agent_Base):
    def __init__(
        self,
        config
    ):
        super().__init__()
        self.platform = config['platform']

    def run_sql(
        self,
        sql: str,
        db_conn
    ) -> list:
        if QUERY_MODE == "ori":
            cursor = db_conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        elif QUERY_MODE == "pd":
            result = pd.read_sql_query(sql, db_conn)
            return result.values.tolist()

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
    def revise(
        self,
        prompt: str,
        llm: LLM_Base,
    ):
        llm_message = [user_message(prompt)]
        response = llm.call(llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        print("="*10,"ANSWER","="*10)
        print(answer)
        new_sql = parse_sql(text=answer)
        return new_sql

    @override
    def chat(
        self,
        message: dict,
        llm: LLM_Base=None,
        db_conn = None
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
                sql_result = self.run_sql(message["sql"],db_conn)
            except Exception as error:
                if QUERY_MODE == "ori":
                    error_str = str(error.args[0])
                    except_flag = True
                elif QUERY_MODE == "pd":
                    error_str = str(error.args[0])
                    error_str = error_str[error_str.index("': ") + 3:]
                    except_flag = True

            if except_flag is False:
                message["message_to"] = MANAGER
                message["sql_result"] = sql_result
                return message
            else:
                prompt = self.create_reviser_prompt(message,error_str)
                new_sql = self.revise(prompt, llm)
                message["sql"] = new_sql
                return message