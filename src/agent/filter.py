from src.exceptions import AgentTypeException
from src.llm.llm_base import LLM_Base
from src.utils.const import FILTER, DECOMPOSER
from src.utils.template import filter_template
from src.utils.timeout import timeout
from src.utils.utils import parse_json, info, user_message
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB


class Filter(Agent_Base):
    def __init__(self):
        super().__init__()

    def get_evidence_str(
        self,
        question: str,
        vectordb: VectorDB,
    ):
        evidence_ids = vectordb.get_related_key_ids(question)
        evidence_set = set()
        evidence_str = ""
        for evidence_id in evidence_ids:
            evidence_set.add(vectordb.get_doc_by_id(evidence_id))
        for evidence in evidence_set:
            evidence_str += "=====\n" + evidence + "\n"
        return evidence_str

    def create_filter_prompt(
        self,
        question: str,
        vectordb: VectorDB,
    ) -> (str,str):
        schema_list = vectordb.get_related_schema(question)
        schema_str = ""
        for schema in schema_list:
            schema_str += "=====" + schema
        evidence_str = self.get_evidence_str(question, vectordb)
        prompt = filter_template.format(schema_str, evidence_str, question)
        info(prompt)
        return prompt,schema_str,evidence_str

    @timeout(180)
    def get_filter_json(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> (dict, str):
        llm_message = [user_message(prompt)]
        ans = llm.submit_message(messages=llm_message)
        info(ans)
        json_ans = parse_json(ans)
        return json_ans

    def prune_schema(
        self,
        json_ans: dict,
        schema_str: str
    ) -> str:
        table_pos = {}
        for key in json_ans:
            table_pos[key] = (schema_str.find("Table: " + key))
        sorted_table_pos = dict(sorted(table_pos.items(), key=lambda item: item[1]))

        table_col = {}
        for key in sorted_table_pos:
            start = schema_str.find("[", sorted_table_pos[key]) + 1
            end = schema_str.find("]", sorted_table_pos[key]) - 2
            table_col[key] = schema_str[start:end].replace('\n(', '').split('),')
        for key in json_ans:
            if json_ans[key] == 'drop_all':
                table_col.pop(key)
            elif json_ans[key] == 'keep_all':
                pass
            else:
                col_list = table_col[key]
                keep_col = json_ans[key]
                new_col_list = []
                for col in col_list:
                    if col[:col.find(',')] in keep_col:
                        new_col_list.append(col)
                table_col[key] = new_col_list

        new_schema = ""
        for table, col_list in table_col.items():
            new_schema += "=====\n"
            new_schema += "Table: " + table + "\n"
            new_schema += "Column: [\n"
            for col in col_list:
                new_schema += "(" + col + "),\n"
            new_schema += ']\n'
        return new_schema

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB= None,
    ):
        if message["message_to"] != FILTER:
            raise AgentTypeException("The message should not be processed by " + FILTER + ". It is sent to " + message["message_to"])
        else:
            info("The message is being processed by " + FILTER + "...")
            prompt,schema_str,evidence_str = self.create_filter_prompt(message["question"], vectordb)
            json_ans = self.get_filter_json(prompt, llm)
            new_schema_str = self.prune_schema(json_ans,schema_str)
            message["schema"] = new_schema_str
            message["evidence"] = evidence_str
            message["message_to"] = DECOMPOSER
            return message