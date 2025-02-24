from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import DECOMPOSER, REVISER
from src.utils.template import decomposer_template, decomposer_hint_template
from src.utils.utils import parse_sql, user_message, get_response_content, timeout


class Decomposer(Agent_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self.platform = config['platform']

    def create_decomposer_prompt(
        self,
        message: dict
    ) -> str:
        dialect = message['dialect']
        schema_str = message['schema']
        hint_str = message['hint']
        question = message['question']
        if hint_str == "":
            prompt = decomposer_template.format(dialect, schema_str, question)
        else:
            prompt = decomposer_template.format(dialect, schema_str, question) + decomposer_hint_template.format(hint_str)
        print("="*10,"PROMPT","="*10)
        print(prompt)
        return prompt

    @timeout(180)
    def get_decomposer_sql(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        print(answer)
        sql = parse_sql(text=answer)
        return sql


    def chat(
        self,
        message: dict,
        llm: LLM_Base = None
    ) -> dict:
        if message["message_to"] != DECOMPOSER:
            raise Exception("The message should not be processed by " + DECOMPOSER + 
                            ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + DECOMPOSER + "...")
            prompt = self.create_decomposer_prompt(message=message)
            sql = self.get_decomposer_sql(prompt=prompt, llm=llm)
            message["sql"] = sql
            message["message_to"] = REVISER
            return message