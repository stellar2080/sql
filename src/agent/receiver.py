from src.agent.agent_base import Agent_Base
from src.llm.llm_base import LLM_Base
from src.utils.const import TOOLS, FUNC_NAMES, FILTER, MANAGER
from src.utils.template import receiver_template
from src.utils.timeout import timeout
from src.utils.utils import info, user_message, get_res_finish_reason, get_res_tool_calls, get_res_content, schema_list_to_str
from src.vectordb.vectordb import VectorDB


class Receiver(Agent_Base):
    def __init__(self):
        super().__init__()

    def create_receiver_prompt_0(
        self,
        question: str,
    ) -> (str, str):
        prompt = receiver_template[0].format(question)
        info(prompt)
        return prompt

    def create_receiver_prompt_1(
        self,
        question: str,
        vectordb: VectorDB,
    ) -> (str, str):
        schema_list = vectordb.get_related_schema(question)
        schema_str = schema_list_to_str(schema_list)
        prompt = receiver_template[1].format(question,schema_str)
        info(prompt)
        return prompt,schema_str

    @timeout(180)
    def get_response(
        self,
        prompt: str,
        llm: LLM_Base,
        receiver_mode: int
    ):
        llm_message = [user_message(prompt)]
        response = llm.call(llm_message, tools=TOOLS[receiver_mode])
        return response

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None,
    ):
        prompt = None
        mode = message["receiver_mode"]

        if mode == 0:
            prompt = self.create_receiver_prompt_0(message["question"])

        elif mode == 1:
            prompt, schema_str = self.create_receiver_prompt_1(message["question"], vectordb)
            message['schema'] = schema_str

        response = self.get_response(prompt, llm, mode)
        info(response)

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
                    message["receiver_mode"] = 1
                    return message

                elif func_name == 'query_database':
                    message['message_to'] = FILTER
                    return message





