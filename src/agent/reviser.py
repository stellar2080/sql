import pandas as pd
from typing_extensions import override

from src.llm.llm_base import LLM_Base
from src.utils.const import REVISER, MANAGER, QUERY_MODE
from src.utils.database_utils import connect_to_sqlite
from src.utils.template import reviser_template
from src.utils.utils import parse_sql, user_message, get_response_content, timeout
from src.agent.agent_base import Agent_Base


class Reviser(Agent_Base):
    def __init__(self,config):
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
        sqlite_error
    ) -> str:
        prompt = reviser_template.format(
            message["schema"],
            message["question"],
            message["hint"],
            message["sql"],
            sqlite_error
        )
        print(prompt)
        return prompt

    @timeout(180)
    def revise(
        self,
        prompt: str,
        llm: LLM_Base,
    ):
        llm_message = [user_message(prompt)]
        response = llm.call(llm_message)
        answer = get_response_content(response, self.platform)
        print(answer)
        new_sql = parse_sql(answer)
        return new_sql

    @override
    def chat(
        self,
        message: dict,
        llm: LLM_Base=None,
        db_conn = None
    ):
        if message["message_to"] != REVISER:
            raise Exception("The message should not be processed by " + REVISER + ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + REVISER + "...")
            sqlite_error = ""
            except_flag = False
            result = None
            try:
                result = self.run_sql(message["sql"],db_conn)
            except Exception as error:
                if QUERY_MODE == "ori":
                    sqlite_error = str(error.args[0])
                    except_flag = True
                elif QUERY_MODE == "pd":
                    sqlite_error = str(error.args[0])
                    sqlite_error = sqlite_error[sqlite_error.index("': ") + 3:]
                    except_flag = True

            if except_flag is False:
                message["message_to"] = MANAGER
                message["sql_result"] = result
                print(result)
                return message
            else:
                prompt = self.create_reviser_prompt(
                    message,
                    sqlite_error,
                )
                new_sql = self.revise(prompt, llm)
                message["sql"] = new_sql
                return message