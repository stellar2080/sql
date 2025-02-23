from src.llm.llm_base import LLM_Base
from src.utils.const import FILTER, DECOMPOSER, F_HINT_THRESHOLD, F_COL_THRESHOLD, F_VAL_THRESHOLD
from src.utils.template import filter_template, filter_hint_template
from src.utils.utils import parse_json, user_message, get_response_content, timeout, \
    get_subsequence_similarity, get_embedding_list, get_cos_similarity, parse_list, lsh
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB


class Filter(Agent_Base):
    def __init__(self, config):
        super().__init__()
        self.platform = config['platform']

    def get_related_hint_list(
        self,
        entity_list: list,
        vectordb: VectorDB,
    ):
        hint_list = []
        hint_ids = vectordb.get_related_key(entity_list, extracts=['distances', 'metadatas'])
        for i in range(len(entity_list)):
            if len(entity_list) == 1:
                distances = hint_ids['distances']
                metadatas = hint_ids['metadatas']
            else:
                distances = hint_ids['distances'][i]
                metadatas = hint_ids['metadatas'][i]
            filtered_ids = [
                metadata['doc_id'] for distance, metadata in sorted(
                    zip(distances, metadatas), key=lambda x: x[0]
                ) if 1 - distance > F_HINT_THRESHOLD
            ]
            # print(filtered_ids)
            if len(filtered_ids) != 0:
                hint_list.extend(vectordb.get_doc_by_id(filtered_ids))

        # print(hint_list)
        return list(dict.fromkeys(hint_list))

    def process_hint_list(
        self,
        hint_list: list,
        entity_list: list,
    ):
        hint_str = ""
        if len(hint_list) != 0:
            for enum, hint in enumerate(hint_list,start=1):
                express_list = parse_list(hint)

                hint_str += f"[{enum}] " + " ".join(express_list) + "\n"

                for i in range(0,len(express_list)):
                    entity = express_list[i]
                    if len(entity) > 1:
                        entity_list.append(entity)
            
        return hint_str, entity_list

    def get_schema(
        self,
        db_conn
    ):
        cur = db_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_names = cur.fetchall()
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        sql_datas = cur.fetchall()

        schema = []

        count = 0
        for enum, tbl_name in enumerate(tbl_names,start=0):
            tbl_name = tbl_name[0]

            cur.execute(f"PRAGMA table_info({tbl_name})")
            col_datas = cur.fetchall()

            cols = []
            for col_data in col_datas:
                cols.append([count, col_data[5], tbl_name, col_data[1], col_data[2]])
                count += 1

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
                    comment_str = sql_str[idx + 3:end]

                    Samples_idx = comment_str.find("Samples:")
                    comment_str = comment_str if Samples_idx == -1 else comment_str[:Samples_idx - 1]

                    comment_str = comment_str.replace("(in Yuan)", "").strip()
                    
                    cols[num].extend([comment_str,None,None,None,False])
                    num += 1
            schema.extend(cols)

        # schema = [[0 enum, 1 pk,2 tbl_name,3 col_name,4 col_type,5 comment,6 value_list,7 fk,8 similarity,9 ischosen],...]
        return schema

    def add_fk_to_schema(
        self,
        schema: list,
        db_conn
    ):
        cur = db_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_names = cur.fetchall()

        for enum, tbl_name in enumerate(tbl_names,start=0):
            tbl_name = tbl_name[0]
            cur.execute(f"PRAGMA foreign_key_list({tbl_name})")
            fk_datas = cur.fetchall()
            for fk_data in fk_datas:
                for col in schema:
                    if tbl_name == col[2] and fk_data[4] == col[3]:
                        col[7] = (fk_data[2], fk_data[3])


    def get_related_column(self, entity_list: list, schema: list, tbl_name_selected: set):
        name_list = []
        comment_list = []
        for col in schema:
            name_list.append(col[3])
            comment_list.append(col[5])

        name_embeddings = get_embedding_list(name_list)
        comment_embeddings = get_embedding_list(comment_list)
        entity_embeddings = get_embedding_list(entity_list)

        for enum, entity in enumerate(entity_list, start=0):
            entity_embedding = entity_embeddings[enum]
            for cnum, col in enumerate(schema, start=0):
                col_name = col[3]
                name_sub_similarity = get_subsequence_similarity(entity, col_name)
                name_cos_similarity = get_cos_similarity(entity_embedding, name_embeddings[cnum])
                comment_cos_similarity = get_cos_similarity(entity_embedding, comment_embeddings[cnum])
                col[8] = (name_sub_similarity,name_cos_similarity,comment_cos_similarity)
                # print(entity, col_name, (name_sub_similarity,name_cos_similarity,comment_cos_similarity))

            col_num_set = set()
            for col in sorted(schema, key=lambda x: x[8][0], reverse=True)[:4]:
                # print(col)
                if col[8][0] > F_COL_THRESHOLD:
                    col_num_set.add(col[0])
            # print("=" * 30,"cos_similarity-col_name")
            for col in sorted(schema, key=lambda x: x[8][1], reverse=True)[:4]:
                # print(col)
                if col[8][1] > F_COL_THRESHOLD:
                    col_num_set.add(col[0])
            # print("=" * 30,"cos_similarity-comment")
            for col in sorted(schema, key=lambda x: x[8][2], reverse=True)[:4]:
                # print(col)
                if col[8][2] > F_COL_THRESHOLD:
                    col_num_set.add(col[0])

            for enum, col in enumerate(schema,start=0):
                if enum in col_num_set:
                    col[9] = True
                    tbl_name_selected.add(col[2])
                    # print(col)

    def get_related_value(self, entity_list: list, schema: list, tbl_name_selected: set, db_conn):
        cur = db_conn.cursor()
        for col in schema:
            if col[4].lower() == 'text':
                cur.execute(f"SELECT {col[3]} FROM {col[2]}")
                value_list = [item[0] for item in cur.fetchall()]

                query_results = lsh(entity_list,value_list)
                if query_results != {}:
                    # print(query_results)
                    value_list = []
                    for key, values in query_results.items():
                        embedding_list = get_embedding_list([key] + values)
                        for enum, value in enumerate(values,start=1):
                            # print(key, value, get_subsequence_similarity(key, value), get_cos_similarity(embedding_list[0], embedding_list[idx]))
                            if get_subsequence_similarity(key, value) > F_VAL_THRESHOLD \
                            or get_cos_similarity(embedding_list[0], embedding_list[enum]) > F_VAL_THRESHOLD:
                                value_list.append(value)
                                
                    if len(value_list) != 0:
                        col[6] = value_list
                        col[9] = True
                        tbl_name_selected.add(col[2])
                        # print(col)

    def sel_pf_keys(self, schema: list, tbl_name_selected: set):
        for col in schema:
            if (col[1] == 1 and col[2] in tbl_name_selected) \
            or (col[7] is not None and col[2] in tbl_name_selected):
                col[9] = True

    def get_schema_str(self, schema: list, tbl_name_selected: set):

        def add_tbl_to_schema_str(tbl_name, schema_str):
            schema_str += "=====\n"
            schema_str += f"Table: {tbl_name}\nColumn:\n"
            return schema_str

        def add_col_to_schema_str(column, schema_str):
            schema_str += "(" + column[3] + ", " + "Comment: " + column[5]
            if column[6] is not None:
                schema_str += ", Sample: " + ",".join(column[6])
            if column[1] == 1:
                schema_str += ", Primary key"
            if column[7] is not None and column[7][0] in tbl_name_selected:
                schema_str += ", Foreign key: references " + column[7][0] + "(" + column[7][1] + ")"
            schema_str += ")\n"
            return schema_str

        schema_str = ""
        tbl_now = None
        for col in schema:
            if (tbl_now is None or tbl_now != col[2]) and col[2] in tbl_name_selected:
                schema_str = add_tbl_to_schema_str(tbl_name=col[2],schema_str=schema_str)
                tbl_now = col[2]
            if col[9]:
                schema_str = add_col_to_schema_str(column=col,schema_str=schema_str)
        
        return schema_str
                
    def create_filter_prompt(
        self,
        schema_str: str,
        hint_str: str,
        question: str,
    ) -> str:
        if hint_str == "":
            prompt = filter_template.format(schema_str, question)
        else:
            prompt = filter_template.format(schema_str, question) + filter_hint_template.format(hint_str)
        print("="*10,"PROMPT","="*10)
        print(prompt)
        return prompt

    @timeout(180)
    def get_filter_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_response_content(response, self.platform)
        print("="*10,"ANSWER","="*10)
        print(answer)
        return answer

    def prune_schema(
        self,
        ans_json: dict,
        schema: list,
        tbl_name_selected: set
    ):
        for col in schema:
            col[9] = False
        tbl_name_selected.clear()

        for key, col_list in ans_json.items():
            if len(col_list) != 0:
                tbl_name_selected.add(key)
                for col in schema:
                    if col[2] == key and col[3] in col_list:
                        col[9] = True

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None,
        db_conn = None
    ):
        if message["message_to"] != FILTER:
            raise Exception("The message should not be processed by " + FILTER +
                            ". It is sent to " + message["message_to"])
        else:
            print("The message is being processed by " + FILTER + "...")
            tbl_name_selected = set()
            hint_list = self.get_related_hint_list(entity_list=message['entity'],vectordb=vectordb)
            hint_str, entity_list = self.process_hint_list(
                hint_list=hint_list, entity_list=message['entity'])
            schema = self.get_schema(db_conn=db_conn)
            self.add_fk_to_schema(schema=schema,db_conn=db_conn)
            self.get_related_column(entity_list=entity_list,schema=schema,tbl_name_selected=tbl_name_selected)
            self.get_related_value(entity_list=entity_list,schema=schema,tbl_name_selected=tbl_name_selected,db_conn=db_conn)
            self.sel_pf_keys(schema=schema, tbl_name_selected=tbl_name_selected)
            schema_str = self.get_schema_str(schema=schema, tbl_name_selected=tbl_name_selected)
            prompt = self.create_filter_prompt(schema_str=schema_str, hint_str=hint_str, question=message['question'])
            ans = self.get_filter_ans(prompt=prompt, llm=llm)
            ans_json = parse_json(ans)
            self.prune_schema(ans_json=ans_json, schema=schema, tbl_name_selected=tbl_name_selected)
            self.sel_pf_keys(schema=schema, tbl_name_selected=tbl_name_selected)
            new_schema_str = self.get_schema_str(schema=schema, tbl_name_selected=tbl_name_selected)
            message["schema"] = new_schema_str
            message["hint"] = hint_str
            message["message_to"] = DECOMPOSER
            return message