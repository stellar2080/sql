from scipy.constants import electron_mass

from src.llm.llm_base import LLM_Base
from src.utils.const import FILTER, DECOMPOSER
from src.utils.database_utils import connect_to_sqlite
from src.utils.template import filter_template
from src.utils.utils import parse_json, user_message, get_res_content, timeout, \
    get_subsequence_similarity, get_embedding_list, get_cos_similarity, parse_list, lsh
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB


class Filter(Agent_Base):
    def __init__(self, config):
        super().__init__()
        self.url = config.get("db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.conn, _ = connect_to_sqlite(self.url, self.check_same_thread)

    def get_evidence_str(
        self,
        entity_list: list,
        vectordb: VectorDB,
    ):
        evidence_list = []
        evidence_str = ""
        evidence_ids = vectordb.get_related_key(entity_list, extracts=['distances', 'metadatas'])
        for i in range(len(entity_list)):
            distances = evidence_ids['distances'][i]
            metadatas = evidence_ids['metadatas'][i]
            filtered_ids = [
                metadata['doc_id'] for distance, metadata in sorted(
                    zip(distances, metadatas), key=lambda x: x[0]
                ) if distance < 0.3
            ]
            # print(filtered_ids)
            if len(filtered_ids) != 0:
                evidence_list.extend(vectordb.get_doc_by_id(filtered_ids))

        # print(evidence_list)
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

    def get_schema(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_names = cur.fetchall()
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        sql_datas = cur.fetchall()

        schema = []

        for enum, tbl_name in enumerate(tbl_names,start=0):
            tbl_name = tbl_name[0]

            cur.execute(f"PRAGMA table_info({tbl_name})")
            col_datas = cur.fetchall()
            cols = [[col_data[5], tbl_name, col_data[1], col_data[2]] for col_data in col_datas]

            sql_str: str = sql_datas[enum][0]
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

        # schema = [[pk,tbl_name,col_name,col_type,comment,similarity],...]
        return schema

    def get_pf_keys(self, schema: list):
        primary_keys = []
        foreign_keys = []
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_names = cur.fetchall()

        for enum, tbl_name in enumerate(tbl_names,start=0):
            tbl_name = tbl_name[0]
            cur.execute(f"PRAGMA foreign_key_list({tbl_name})")
            foreign_col_datas = cur.fetchall()
            for foreign_col in foreign_col_datas:
                foreign_keys.append([[tbl_name, foreign_col[4]], [foreign_col[2], foreign_col[3]]])

        for item in schema:
            if item[0] == 1:
                primary_keys.append(item[:5])
            for foreign_key in foreign_keys:
                if foreign_key[0][0] == item[1] and foreign_key[0][1] == item[2]:
                    foreign_key[0] = item[:5]
                elif foreign_key[1][0] == item[1] and foreign_key[1][1] == item[2]:
                    foreign_key[1] = item[:5]

        # pk = [[pk,tbl_name,col_name,col_type,comment],...]
        # fk = [[[tbl_name,col_name],[refer_tbl_name,refer_col_name]],...]
        return primary_keys, foreign_keys

    def get_related_column(self, entity_list: list, schema, primary_keys, foreign_keys):
        column_set = set()
        tbl_name_set = set()

        name_embeddings = get_embedding_list([col[2].lower().replace('_',' ').replace('-',' ') for col in schema])
        comment_embeddings = get_embedding_list([col[4].lower().replace('_',' ').replace('-',' ') for col in schema])
        entity_embeddings = get_embedding_list(entity_list)

        for e_idx, entity in enumerate(entity_list, start=0):
            entity_embedding = entity_embeddings[e_idx]
            for c_idx, col in enumerate(schema, start=0):
                col_name = col[2]
                s_similarity = get_subsequence_similarity(entity, col_name)
                name_cos_similarity = get_cos_similarity(entity_embedding, name_embeddings[c_idx])
                comment_cos_similarity = get_cos_similarity(entity_embedding, comment_embeddings[c_idx])
                col[5] = (s_similarity,name_cos_similarity,comment_cos_similarity)
                # print(entity, col_name, (s_similarity,name_cos_similarity,comment_cos_similarity))

            print("=" * 20)
            print(entity)
            print("="*30,"subsequence_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[5][0], reverse=True)[:4]:
                print(item)
                if item[5][0] > 0.8:
                    tbl_name_set.add(item[1])
                    column_set.add(tuple(item[:5]))
            print("=" * 30,"cos_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[5][1], reverse=True)[:4]:
                print(item)
                if item[5][1] > 0.8:
                    tbl_name_set.add(item[1])
                    column_set.add(tuple(item[:5]))
            print("=" * 30,"cos_similarity-comment")
            for item in sorted(schema, key=lambda x: x[5][2], reverse=True)[:4]:
                print(item)
                if item[5][2] > 0.8:
                    tbl_name_set.add(item[1])
                    column_set.add(tuple(item[:5]))


        for primary_key in primary_keys:
            if primary_key[1] in tbl_name_set:
                column_set.add(tuple(primary_key))

        i = 0
        while i < len(foreign_keys):
            foreign_key = foreign_keys[i]
            if foreign_key[0][1] in tbl_name_set and foreign_key[1][1] in tbl_name_set:
                column_set.add(tuple(foreign_key[0]))
                column_set.add(tuple(foreign_key[1]))
                i += 1
            else:
                foreign_keys.remove(foreign_key)

        foreign_keys.sort(key=lambda x: x[0][1])

        # column_set = {(pk,tbl_name,col_name,col_type,comment),...}
        return column_set, foreign_keys


    # def get_related_value(self, entity_list: list, schema: list, column_set: set):
    #     cur = self.conn.cursor()
    #     for item in schema:
    #         if item[3] == 'TEXT':
    #             cur.execute(f"SELECT {item[2]} FROM {item[1]}")
    #             value_list = [item[0] for item in cur.fetchall()]
    #             query_results = lsh(entity_list,value_list)
    #             if query_results != {}:
    #                 for key, values in query_results.items():
    #                     embedding_list = get_embedding_list(values.copy().insert(0,key))
    #                     for idx, value in enumerate(values,start=1):
    #                         if get_subsequence_similarity(key, value) > 0.8:
    #                             if get_cos_similarity(embedding_list[0], embedding_list[idx]) > 0.8:
    #                                 column_set.add(item[:5] + )
    #             else:



    def get_related_entity(self, entity_list: list, schema: list, primary_keys, foreign_keys):
        column_set, foreign_keys = self.get_related_column(entity_list, schema, primary_keys, foreign_keys)
        # column_set = self.get_related_value(entity_list, schema, column_set)

        column_list = sorted(list(column_set), key=lambda x: x[1])
        return column_list


    def get_schema_str(self, column_list: list, foreign_keys: list):
        tbl_name = column_list[0][1]
        schema_str = "=====\n"
        schema_str += f"Table: {tbl_name}\nColumn: [\n"
        idx = 0

        for column in column_list:
            if column[1] == tbl_name:
                schema_str += "(" + column[2] + ", " + "Comment: "+ column[4] + ", Type: " + column[3]
                if column[0] == 1:
                    schema_str += ", Primary key"
                schema_str +=  ")\n"

            else:
                for i in range(idx, len(foreign_keys)):
                    foreign_key = foreign_keys[i]
                    if foreign_key[0][1] == tbl_name:
                        schema_str += ("Foreign key: " + foreign_key[0][2] + " References " +
                                       foreign_key[1][1] + "(" + foreign_key[1][2] + ")\n")
                    else:
                        idx = i
                        break
                tbl_name = column[1]
                schema_str += "]\n"


                schema_str += "=====\n"
                schema_str += f"Table: {tbl_name}\nColumn: [\n"
                schema_str += "(" + column[2] + ", " + "Comment: " + column[4] + ", Type: " + column[3]
                if column[0] == 1:
                    schema_str += ", Primary key"
                schema_str +=  ")\n"

        for i in range(idx, len(foreign_keys)):
            foreign_key = foreign_keys[i]
            if foreign_key[0][1] == tbl_name:
                schema_str += ("Foreign key: " + foreign_key[0][2] + " References " +
                               foreign_key[1][1] + "(" + foreign_key[1][2] + ")\n")
        schema_str += "]\n"
        return schema_str

    def create_filter_prompt(
        self,
        entity_list: list,
        question: str,
        vectordb: VectorDB,
    ) -> (str,str,str):
        # print(entity_list)
        evidence_str, entity_list = self.get_evidence_str(entity_list, vectordb)
        # print(entity_list)
        schema = self.get_schema()
        # print(schema)
        primary_keys, foreign_keys = self.get_pf_keys(schema)
        # print(primary_keys, foreign_keys)
        column_list = self.get_related_entity(entity_list, schema, primary_keys, foreign_keys)
        # print(column_list, foreign_keys)
        schema_str = self.get_schema_str(column_list, foreign_keys)
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
            raise Exception("The message should not be processed by " + FILTER +
                            ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + FILTER + "...")
            prompt, schema_str, evidence_str = self.create_filter_prompt(
                message["extract"], message['question'], vectordb
            )
            ans = self.get_filter_ans(prompt, llm)
            json_ans = parse_json(ans)

            if isinstance(json_ans,dict):
                new_schema_str = self.prune_schema(json_ans,schema_str)
                message["schema"] = new_schema_str
                message["evidence"] = evidence_str
                message["message_to"] = DECOMPOSER
                return message

            raise Exception("Error parsing json: "+json_ans)