from src.agent.agent_base import Agent_Base
from src.exceptions import AgentTypeException
from src.llm.llm_base import LLM_Base
from src.utils.const import DECOMPOSER, REVISER
from src.utils.template import decompose_template
from src.utils.timeout import timeout
from src.utils.utils import parse_sql, info, user_message, get_res_content


class Decomposer(Agent_Base):
    def __init__(self):
        super().__init__()

    def create_decomposer_prompt(
        self,
        message: dict
    ) -> str:
        prompt = decompose_template.format(message["schema"],message["evidence"],message["question"])
        info(prompt)
        return prompt

    @timeout(180)
    def get_decomposer_sql(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        message = [user_message(prompt)]
        response = llm.call(messages=message)
        answer = get_res_content(response)
        info(answer)
        sql = parse_sql(answer)
        return sql


    def chat(
        self,
        message: dict,
        llm: LLM_Base = None
    ):
        if message["message_to"] != DECOMPOSER:
            raise AgentTypeException("The message should not be processed by " + DECOMPOSER + ". It is sent to " + message["message_to"])
        else:
            info("The message is being processed by " + DECOMPOSER + "...")
            prompt = self.create_decomposer_prompt(message)
            sql = self.get_decomposer_sql(prompt, llm)
            message["sql"] = sql
            message["message_to"] = REVISER
            return message