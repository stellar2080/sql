from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import TOOLS, FUNC_NAMES, FILTER, MANAGER
from src.utils.template import receiver_template
from src.utils.timeout import timeout
from src.utils.utils import info, user_message, get_res_finish_reason, get_res_tool_calls, get_res_content, \
    assistant_message
from src.vectordb.vectordb import VectorDB


class Receiver(Agent_Base):
    def __init__(self):
        super().__init__()

    def get_mem_string(
        self,
        assiatant_str: str,
        result
    ):
        if isinstance(result, list):
            result = str(result)
        string = "【SQL】\n" + assiatant_str + "\n【SQL_result】\n" + result

        return string

    def get_mem_message(
        self,
        question: str,
        vectordb: VectorDB
    ) -> list:
        memories = vectordb.get_related_memory(question)
        llm_message = []
        for item in memories:
            llm_message.append(user_message(item['user']))
            if 'result' not in item.keys():
                llm_message.append(assistant_message(item['assistant']))
            else:
                string = self.get_mem_string(item['assistant'], item['result'])
                llm_message.append(assistant_message(string))

        return llm_message

    def create_llm_message(
        self,
        question: str,
        vectordb: VectorDB
    ):
        llm_message = self.get_mem_message(question, vectordb)
        prompt = receiver_template.format(question)
        llm_message.append(user_message(prompt))
        info(llm_message)

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





