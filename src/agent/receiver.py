from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import TOOLS
from src.utils.template import receiver_template_0, receiver_template_1
from src.utils.utils import info, user_message


class Receiver(Agent_Base):
    def __init__(self):
        super().__init__()

    def create_receiver_prompt(
        self,
        question: str,
        template_type: int
    ) -> (str, str):
        prompt = ""
        if template_type == 0:
            prompt = receiver_template_0.format(question)
        elif template_type == 1:
            prompt = receiver_template_1.format(question)
        info(prompt)
        return prompt

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
    ):
        prompt = self.create_receiver_prompt(message["question"],template_type=0)
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message,tools=TOOLS)
        info(response)
