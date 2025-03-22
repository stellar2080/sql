from client.agent.agent_base import Agent_Base
from client.llm.llm_base import LLM_Base
from client.utils.const import GENERATOR, REVISER
from client.utils.template import generator_template_p1, generator_hint_template, generator_template_p2
from client.utils.utils import parse_list, parse_sql, user_message, get_response_content, timeout
from client.vectordb.vectordb import VectorDB

class Generator(Agent_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self.platform = config.get('platform','')
        self.user_id = config.get('user_id','')
        self.G_HINT_THRESHOLD = config.get('G_HINT_THRESHOLD')

    def get_rela_tips(
        self,
        question: str,
        vectordb: VectorDB,
    ) -> list:
        tips = vectordb.get_related_tip(
            query_texts=question, 
            user_id=self.user_id, 
            extracts=['distances', 'documents']
        )
        distances = tips['distances']
        documents = tips['documents']
        tip_list = [
            document for distance, document in sorted(
                zip(distances, documents), key=lambda x: x[0]
            ) if 1 - distance > self.G_HINT_THRESHOLD
        ]
        return tip_list

    def get_hint_str(
        self,
        hint_list: list,
        tip_list: list,
    ) -> str:
        hint_list.extend(tip_list)
        # print(hint_list)
        hint_str = ""
        if len(hint_list) != 0:
            for enum, hint in enumerate(hint_list,start=1):
                hint_str += f"[{enum}] " + hint + "\n"

        return hint_str

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
        print("="*10,"PROMPT","="*10)
        print(prompt)
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
        print("="*10,"ANSWER","="*10)
        print(answer)
        sql = parse_sql(text=answer)
        return sql


    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None
    ) -> dict:
        if message["message_to"] != GENERATOR:
            raise Exception("The message should not be processed by " + GENERATOR + 
                            ". It is sent to " + message["message_to"])
        else:
            # print("The message is being processed by " + GENERATOR + "...")
            question = message['question']
            hint_list = message["hint"]
            tip_list = self.get_rela_tips(question=question, vectordb=vectordb)
            hint_str = self.get_hint_str(hint_list=hint_list, tip_list=tip_list)
            message['hint'] = hint_str
            prompt = self.create_generator_prompt(message=message)
            sql = self.get_generator_sql(prompt=prompt, llm=llm)
            message["sql"] = sql
            message["message_to"] = REVISER
            return message