from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import TOOLS, FUNC_NAMES, FILTER, MANAGER
from src.utils.template import receiver_template, memory_template_0, memory_template_1
from src.utils.timeout import timeout
from src.utils.utils import info, user_message, get_res_finish_reason, get_res_tool_calls, get_res_content
from src.vectordb.vectordb import VectorDB


class Receiver(Agent_Base):
    def __init__(self):
        super().__init__()
        self.mem_prompt = ""

    def add_mem_string(
        self,
        count: int,
        question: str,
        answer: str,
        result = None,
    ):
        if result is None:
            self.mem_prompt += memory_template_0.format(count, question, answer)
        else:
            if isinstance(result, list):
                result = str(result)
            self.mem_prompt += memory_template_1.format(count, question, answer, result)

    def get_mem_prompt(
        self,
        question: str,
        vectordb: VectorDB
    ):
        memories = vectordb.get_related_memory(question)
        count = 1
        for item in memories:
            if 'result' in item.keys():
                self.add_mem_string(count, item['user'], item['assistant'], item['result'])
            else:
                self.add_mem_string(count, item['user'], item['assistant'])
            count += 1

    def create_llm_message(
        self,
        question: str,
        vectordb: VectorDB
    ):
        self.get_mem_prompt(question, vectordb)
        prompt = receiver_template.format(self.mem_prompt,question)
        info(prompt)
        llm_message = [user_message(prompt)]

        return llm_message

    @timeout(180)
    def get_response(
        self,
        llm_message: list,
        llm: LLM_Base
    ):
        response = llm.call(llm_message, tools=TOOLS)
        return response

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None,
    ):

        llm_message = self.create_llm_message(message["question"],vectordb)
        response = self.get_response(llm_message, llm)
        finish_reason = get_res_finish_reason(response)

        if finish_reason == "stop":
            message["response"] = get_res_content(response)
            message['message_to'] = MANAGER
            return message

        elif finish_reason == "tool_calls":
            tool_calls = get_res_tool_calls(response)

            if tool_calls is None:
                raise Exception("No tool calls found.")

            else:
                info(tool_calls)
                func_name = tool_calls[0]['function']['name']

                if func_name not in FUNC_NAMES:
                    raise Exception("The called function was not found")

                elif func_name == 'query_database':
                    message['message_to'] = FILTER
                    return message





