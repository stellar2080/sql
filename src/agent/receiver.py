from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import TOOLS, FUNC_NAMES, FILTER, MANAGER
from src.utils.template import receiver_template
from src.utils.timeout import timeout
from src.utils.utils import info, user_message, get_res_finish_reason, get_res_tool_calls, get_res_content
from src.vectordb.vectordb import VectorDB


class Receiver(Agent_Base):
    def __init__(self):
        super().__init__()

    def create_receiver_prompt(
        self,
        question: str,
    ):
        prompt = receiver_template.format(question)
        info(prompt)
        return prompt

    @timeout(180)
    def get_response(
        self,
        prompt: str,
        llm: LLM_Base
    ):
        llm_message = [user_message(prompt)]
        response = llm.call(llm_message, tools=TOOLS)
        return response

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None,
    ):
        prompt = self.create_receiver_prompt(message["question"])

        response = self.get_response(prompt, llm)

        finish_reason = get_res_finish_reason(response)

        if finish_reason == "stop":
            message["result"] = get_res_content(response)
            message['message_to'] = MANAGER
            return message

        elif finish_reason == "tool_calls":
            tool_calls = get_res_tool_calls(response)

            if tool_calls is None:
                raise Exception("No tool calls found.")

            elif len(tool_calls) == 1:
                info(tool_calls)
                func_name = tool_calls[0]['function']['name']

                if func_name not in FUNC_NAMES:
                    raise Exception("The called function was not found")

                elif func_name == 'get_schema':
                    message['message_to'] = FILTER
                    return message





