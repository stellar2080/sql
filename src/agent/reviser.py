import os
import sqlite3
from urllib.parse import urlparse

import pandas as pd
import requests
from typing_extensions import override

from src.exceptions import AgentTypeException, DbConnException
from src.llm.llm_base import LLM_Base
from src.utils.const import REVISER, MANAGER
from src.utils.template import reviser_template
from src.utils.timeout import timeout
from src.utils.utils import parse_sql, info
from src.agent.agent_base import Agent_Base


class Reviser(Agent_Base):
    def __init__(self,config=None):
        if config is None:
            config = {}
        self.config = config
        self.conn = None
        self.dialect = None
        url = config.get("db_path",'.')
        check_same_thread = config.get("check_same_thread", False)
        self.connect_to_sqlite(url=url,check_same_thread=check_same_thread)

    def create_reviser_prompt(
        self,
        schema_str: str,
        question: str,
        sql: str,
        sqlite_error,
        error_class
    ) -> str:
        prompt = reviser_template.format(question, schema_str, sql, sqlite_error, error_class)
        print(prompt)
        return prompt

    @timeout(180)
    def revise(
        self,
        prompt: str,
        llm: LLM_Base,
    ):
        message = [llm.user_message(prompt)]
        ans = llm.submit_message(message)
        print(ans)
        new_sql = parse_sql(ans)
        return new_sql

    def connect_to_sqlite(
        self,
        url: str,
        check_same_thread: bool = False,
        **kwargs
    ):
        if not os.path.exists(url):
            path = os.path.basename(urlparse(url).path)
            response = requests.get(url)
            response.raise_for_status()  # Check that the request was successful
            with open(path, "wb") as f:
                f.write(response.content)
        self.conn = sqlite3.connect(
            url,
            check_same_thread=check_same_thread,
            **kwargs
        )
        self.dialect = "SQLite"

    def is_conn(self):
        return self.conn is not None

    def run_sql(
        self,
        sql: str,
        func: int = 0
    ):
        if self.is_conn() is False:
            raise DbConnException("Please connect to database first.")
        if func == 0:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        elif func == 1:
            result = pd.read_sql_query(sql, self.conn)
            return result

    @override
    def chat(
        self,
        message: dict,
        llm: LLM_Base=None
    ):
        if message["message_to"] != REVISER:
            raise AgentTypeException("The message should not be processed by " + REVISER + ". It is sent to " + message["message_to"])
        else:
            info("The message is being processed by " + REVISER + "...")
            sqlite_error = ""
            error_class = ""
            except_flag = False
            result = None
            try:
                result = self.run_sql(message["sql"])
            except (sqlite3.Error,Exception) as error:
                sqlite_error = str(error.args)
                error_class = str(error.__class__)
                except_flag = True

            if except_flag is False:
                message["message_to"] = MANAGER
                message["result"] = result
                return message
            else:
                prompt = self.create_reviser_prompt(
                    message["schema"],
                    message["question"],
                    message["sql"],
                    sqlite_error,
                    error_class)
                new_sql = self.revise(prompt, llm)
                message["sql"] = new_sql
                return message
