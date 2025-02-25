from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import GENERATOR, REVISER
from src.utils.template import generator_template_p1, generator_hint_template, generator_template_p2
from src.utils.utils import parse_sql, user_message, get_response_content, timeout


class Generator(Agent_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self.platform = config['platform']

    def create_generator_prompt(
        self,
        message: dict
    ) -> str:
        dialect = message['dialect']
        schema_str = message['schema']
        hint_str = message['hint']
        question = message['question']
        if hint_str == "":
            prompt = generator_template_p1.format(dialect, schema_str, question) + generator_template_p2
        else:
            prompt = generator_template_p1.format(dialect, schema_str, question) + \
            generator_hint_template.format(hint_str) + generator_template_p2
        # print("="*10,"PROMPT","="*10)
        # print(prompt)
        return prompt

    @timeout(90)
    def get_generator_sql(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        # print("="*10,"ANSWER","="*10)
        # print(answer)
        sql = parse_sql(text=answer)
        return sql


    def chat(
        self,
        message: dict,
        llm: LLM_Base = None
    ) -> dict:
        if message["message_to"] != GENERATOR:
            raise Exception("The message should not be processed by " + GENERATOR + 
                            ". It is sent to " + message["message_to"])
        else:
            # print("The message is being processed by " + GENERATOR + "...")
            prompt = self.create_generator_prompt(message=message)
            sql = self.get_generator_sql(prompt=prompt, llm=llm)
            message["sql"] = sql
            message["message_to"] = REVISER
            return message