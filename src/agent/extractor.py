from src.llm.llm_base import LLM_Base
from src.utils.const import EXTRACTOR, FILTER
from src.utils.template import extractor_template
from src.utils.utils import user_message, get_res_content, timeout
from src.agent.agent_base import Agent_Base


class Extractor(Agent_Base):
    def __init__(self):
        super().__init__()

    def create_extractor_prompt(
        self,
        question: str,
    ) -> (str,str):
        prompt = extractor_template.format(question)
        print(prompt)
        return prompt

    @timeout(180)
    def get_extractor_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> (dict, str):
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_res_content(response)
        print(answer)
        return answer

    def parse_list(self, string):
        try:
            start = string.rfind('[')
            end = string.rfind(']')
            if start == -1 or end == -1:
                return list(string[start:end+1])
        except Exception as e:
            print(e)

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None
    ):
        if message["message_to"] != EXTRACTOR:
            raise Exception("The message should not be processed by " + EXTRACTOR + ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + EXTRACTOR + "...")
            prompt = self.create_extractor_prompt(message["question"])
            ans = self.get_extractor_ans(prompt, llm)
            list_ans = self.parse_list(ans)
            message["extract"] = list_ans
            message["message_to"] = FILTER
