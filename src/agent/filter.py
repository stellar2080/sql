from scipy.constants import electron_mass

from src.llm.llm_base import LLM_Base
from src.utils.const import FILTER, DECOMPOSER
from src.utils.database_utils import connect_to_sqlite
from src.utils.template import filter_template
from src.utils.utils import parse_json, user_message, get_res_content, timeout, \
    get_subsequence_similarity, get_embedding_list, get_cos_similarity, parse_list
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB


class Filter(Agent_Base):
    def __init__(self, config):
        super().__init__()
        self.url = config.get("db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.conn, _ = connect_to_sqlite(self.url, self.check_same_thread)

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
            cols = [[tbl_name[0], col_data[1], col_data[2]] for col_data in col_datas]
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
                    sub_str = sub_str if Samples_idx == -1 else sub_str[:Samples_idx - 1]

                    sub_str = sub_str.replace("(in Yuan)", "")

                    sub_str = sub_str.strip()

                    cols[num].append(sub_str)
                    cols[num].append(())
                    num += 1
            schema.extend(cols)
        return schema

    def get_evidence_str(
        self,
        entity_list: list,
        vectordb: VectorDB,
    ):
        evidence_list = []
        evidence_str = ""
        for entity in entity_list:
            evidence_ids = vectordb.get_related_key(entity,extracts=['distances','metadatas'])
            filtered_ids = [
                metadata['doc_id'] for distance, metadata in sorted(
                    zip(evidence_ids['distances'],evidence_ids['metadatas']),key=lambda x: x[0]
                ) if distance < 0.3
            ]
            print(filtered_ids)
            for evidence_id in filtered_ids:
                evidence_list.append(vectordb.get_doc_by_id(evidence_id))
        evidence_list = list(dict.fromkeys(evidence_list))
        str_set = set()
        for evidence in evidence_list:
            str_list = parse_list(evidence)
            str_set.add(str_list[0])
            for string in str_list:
                if len(string) > 1:
                    entity_list.append(string)
            evidence_str += "=====\n" + " ".join(str_list) + "\n"
        entity_list = list(set(entity_list) - str_set)
        return evidence_str, entity_list

    def get_related_column(self, entity_list: list):
        column_set = set()

        schema = self.get_schema()
        name_embeddings = get_embedding_list([col[1].lower().replace('_',' ').replace('-',' ') for col in schema])
        comment_embeddings = get_embedding_list([col[3].lower().replace('_',' ').replace('-',' ') for col in schema])
        entity_embeddings = get_embedding_list(entity_list)

        for e_idx, entity in enumerate(entity_list, start=0):
            entity_embedding = entity_embeddings[e_idx]
            for c_idx, col in enumerate(schema, start=0):
                col_name = col[1]
                s_similarity = get_subsequence_similarity(entity, col_name)
                name_cos_similarity = get_cos_similarity(entity_embedding, name_embeddings[c_idx])
                comment_cos_similarity = get_cos_similarity(entity_embedding, comment_embeddings[c_idx])
                col[4] = (s_similarity,name_cos_similarity,comment_cos_similarity)
                # print(entity, col_name, (edit_distance,s_similarity,name_cos_similarity,comment_cos_similarity))

            # print("=" * 20)
            # print(entity)
            # print("="*30,"subsequence_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[4][0], reverse=True)[:5]:
                print(item)
                if item[4][0] > 0.8:
                    column_set.add(tuple(item[:4]))
            # print("=" * 30,"cos_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[4][1], reverse=True)[:5]:
                print(item)
                if item[4][1] > 0.8:
                    column_set.add(tuple(item[:4]))
            # print("=" * 30,"cos_similarity-comment")
            for item in sorted(schema, key=lambda x: x[4][2], reverse=True)[:5]:
                print(item)
                if item[4][2] > 0.8:
                    column_set.add(tuple(item[:4]))

        return sorted(list(column_set),key=lambda x: x[0])


    def get_schema_str(self, column_list: list):
        tbl_name = column_list[0][0]
        schema_str = "=====\n"
        schema_str += f"Table: {tbl_name}\nColumn: [\n"
        for column in column_list:
            if column[0] == tbl_name:
                schema_str += "(" + column[1] + ", " + "Comment: "+ column[3] + ", Type: " + column[2] +  ")\n"
            else:
                tbl_name = column[0]
                schema_str += "]\n"
                schema_str += "=====\n"
                schema_str += f"Table: {tbl_name}\nColumn: [\n"
                schema_str += "(" + column[1] + ", " + "Comment: " + column[3] + ", Type: " + column[2] + ")\n"
        schema_str += "]\n"
        return schema_str

    def create_filter_prompt(
        self,
        entity_list: list,
        question: str,
        vectordb: VectorDB,
    ) -> (str,str,str):
        print(entity_list)
        evidence_str, entity_list = self.get_evidence_str(entity_list, vectordb)
        print(entity_list)
        column_list = self.get_related_column(entity_list)
        print(column_list)
        schema_str = self.get_schema_str(column_list)
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
            if json_ans[key] == 'drop':
                table_col.pop(key)
            elif json_ans[key] == 'keep':
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
        vectordb: VectorDB = None
    ):
        if message["message_to"] != FILTER:
            raise Exception("The message should not be processed by " + FILTER + ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + FILTER + "...")
            prompt, schema_str, evidence_str = self.create_filter_prompt(message["extract"], message['question'], vectordb)
            ans = self.get_filter_ans(prompt, llm)
            json_ans = parse_json(ans)

            if isinstance(json_ans,dict):
                new_schema_str = self.prune_schema(json_ans,schema_str)
                message["schema"] = new_schema_str
                message["evidence"] = evidence_str
                message["message_to"] = DECOMPOSER
                return message

            raise Exception("Error parsing json: "+json_ans)