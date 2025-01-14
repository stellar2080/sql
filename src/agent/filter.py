from src.llm.llm_base import LLM_Base
from src.utils.const import FILTER, DECOMPOSER
from src.utils.database_utils import connect_to_sqlite
from src.utils.template import filter_template
from src.utils.utils import parse_json, user_message, get_res_content, timeout, get_levenshtein_distance, \
    get_subsequence_similarity
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB

from chromadb.utils import embedding_functions


class Filter(Agent_Base):
    def __init__(self, config):
        super().__init__()
        self.url = config.get("db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.conn, _ = connect_to_sqlite(self.url, self.check_same_thread)

    def schema_list_to_str(self,schema_list):
        schema_str = ""
        for schema in schema_list:
            schema_str += "=====" + schema
        return schema_str

    def get_evidence_str(
        self,
        question: str,
        vectordb: VectorDB,
    ):
        evidence_ids = vectordb.get_related_key_meta(question)
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
        schema_str = self.schema_list_to_str(schema_list)
        evidence_str = self.get_evidence_str(question, vectordb)
        prompt = filter_template.format(schema_str, evidence_str, question)
        print(prompt)
        return prompt,schema_str,evidence_str

    @timeout(180)
    def get_filter_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> (dict, str):
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_res_content(response)
        print(answer)
        return answer

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

    def get_schema(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_names = cur.fetchall()
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        sql_datas = cur.fetchall()

        schema = []
        for tbl_name in tbl_names:
            cur.execute(f"PRAGMA table_info('{tbl_name[0]}')")
            col_datas = cur.fetchall()
            cols = [[0, 0, 0, tbl_name[0], col_data[1], col_data[2]] for col_data in col_datas]
            sql_str: str = sql_datas[tbl_names.index(tbl_name)][0]
            start = 0
            num = 0
            while True:
                idx = sql_str.find("-- ", start)
                if idx == -1:
                    break
                else:
                    end = sql_str.find("\n", idx)
                    start = end + 2
                    sub_str = sql_str[idx + 3:end]
                    Samples_idx = sub_str.find("Samples:")
                    cols[num].append(sub_str if Samples_idx == -1 else sub_str[:Samples_idx - 1])
                    num += 1
            schema.extend(cols)
        return schema

    def get_related_column(self, entity_list: list):
        schema = self.get_schema()
        for entity in entity_list:
            for col in schema:
                col_name = col[4]
                edit_distance = get_levenshtein_distance(entity, col_name)
                similarity = get_subsequence_similarity(entity, col_name)
                col[0] = edit_distance
                col[1] = similarity
            print(sorted(schema, key=lambda x: x[0], reverse=False)[:5])
            print(sorted(schema, key=lambda x: x[1], reverse=True)[:5])


    # def get_embedding_list(self, col_list):
    #     embedding_func = embedding_functions.DefaultEmbeddingFunction()


    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None
    ):
        if message["message_to"] != FILTER:
            raise Exception("The message should not be processed by " + FILTER + ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + FILTER + "...")
            prompt, schema_str, evidence_str = self.create_filter_prompt(message["question"], vectordb)
            ans = self.get_filter_ans(prompt, llm)
            json_ans = parse_json(ans)

            if isinstance(json_ans,dict):
                new_schema_str = self.prune_schema(json_ans,schema_str)
                message["schema"] = new_schema_str
                message["evidence"] = evidence_str
                message["message_to"] = DECOMPOSER
                return message

            raise Exception("Error parsing json: "+json_ans)