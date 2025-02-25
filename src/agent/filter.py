from src.llm.llm_base import LLM_Base
from src.utils.const import FILTER, GENERATOR, F_HINT_THRESHOLD, F_COL_THRESHOLD, F_VAL_THRESHOLD
from src.utils.template import filter_template, filter_hint_template
from src.utils.utils import parse_json, user_message, get_response_content, timeout, \
    get_subsequence_similarity, get_embedding_list, get_cos_similarity, parse_list, lsh
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB
import spacy

class Filter(Agent_Base):
    def __init__(self, config):
        super().__init__()
        self.platform = config['platform']

    def parse_nouns(
        self,
        question: str
    ) -> list:
        noun_set = set()
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(question)
        for token in doc:
            if token.pos_ == 'NOUN':
                noun_set.add(token.text)
        noun_list = list(noun_set)
        return noun_list

    def get_related_hint_list(
        self,
        entity_list: list,
        vectordb: VectorDB,
        threshold: float = None
    ) -> list:
        if threshold is None:
            threshold = F_HINT_THRESHOLD
        hint_list = []
        hint_ids = vectordb.get_related_key(query_texts=entity_list, extracts=['distances', 'metadatas'])
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
                ) if 1 - distance > threshold
            ]
            
            if len(filtered_ids) != 0:
                doc_list = vectordb.get_doc_by_id(embedding_ids=filtered_ids)
                hint_list.extend(doc_list)

        distinct_hint_list = list(dict.fromkeys(hint_list))
        return distinct_hint_list

    def process_hint_list(
        self,
        hint_list: list,
        entity_list: list,
    ) -> tuple[str, list]:
        hint_str = ""
        if len(hint_list) != 0:
            for enum, hint in enumerate(hint_list,start=1):
                express_list = parse_list(hint)
                expression = " ".join(express_list)
                hint_str += f"[{enum}] " + expression + "\n"

                for i in range(0, len(express_list)):
                    entity = express_list[i]
                    if len(entity) > 1:
                        entity_list.append(entity)
            
        return hint_str, entity_list

    def get_schema(
        self,
        db_conn
    ) -> list:
        cur = db_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_name_datas = cur.fetchall()
        tbl_names = [tbl_name_data[0] for tbl_name_data in tbl_name_datas]
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        sql_datas = cur.fetchall()
        sql_strs = [sql_data[0] for sql_data in sql_datas]

        schema = []

        index = 0
        for enum, tbl_name in enumerate(tbl_names,start=0):
            cur.execute(f"PRAGMA table_info({tbl_name})")
            col_datas = cur.fetchall()

            columns = []
            for col_data in col_datas:
                is_primary_key = col_data[5]
                col_name = col_data[1]
                col_type = col_data[2]
                columns.append([index, is_primary_key, tbl_name, col_name, col_type])
                index += 1

            sql_str = sql_strs[enum]
            point_now = 0
            num = 0
            while True:
                start = sql_str.find("-- ", point_now)
                if start == -1:
                    break
                else:
                    end = sql_str.find("\n", start)
                    point_now = end + 2
                    comment_str = sql_str[start + 3:end]
                    Samples_idx = comment_str.find("Samples:")
                    comment_str = comment_str if Samples_idx == -1 else comment_str[:Samples_idx - 1]
                    comment_str = comment_str.replace("(in Yuan)", "")
                    comment_str = comment_str.strip()
                    columns[num].extend([comment_str,None,None,None,False])
                    num += 1
            schema.extend(columns)

        # schema = [[0 index, 1 pk,2 tbl_name,3 col_name,4 col_type,5 comment,6 value_list,7 fk,8 similarity,9 ischosen],...]
        return schema

    def add_fk_to_schema(
        self,
        schema: list,
        db_conn
    ):
        cur = db_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbl_name_datas = cur.fetchall()
        tbl_names = [tbl_name_data[0] for tbl_name_data in tbl_name_datas]

        for tbl_name in tbl_names:
            cur.execute(f"PRAGMA foreign_key_list({tbl_name})")
            fk_datas = cur.fetchall()
            for fk_data in fk_datas:
                fk_col_name = fk_data[3]
                for column in schema:
                    column_tbl_name = column[2]
                    column_col_name = column[3]
                    if tbl_name == column_tbl_name and fk_col_name == column_col_name:
                        ref_tbl_name = fk_data[2]
                        ref_col_name = fk_data[4]
                        column[7] = (ref_tbl_name, ref_col_name)


    def get_related_column(
        self, 
        entity_list: list, 
        schema: list, 
        tbl_name_selected: set,
        threshold: float = None
    ):
        if threshold is None:
            threshold = F_COL_THRESHOLD
        col_name_list = []
        comment_list = []
        for column in schema:
            col_name = column[3]
            comment = column[5]
            col_name_list.append(col_name)
            comment_list.append(comment)

        entity_embeddings = get_embedding_list(entity_list)
        col_name_embeddings = get_embedding_list(col_name_list)
        comment_embeddings = get_embedding_list(comment_list)
        
        for enum, entity in enumerate(entity_list, start=0):
            entity_embedding = entity_embeddings[enum]
            for cnum, column in enumerate(schema, start=0):
                col_name = column[3]
                name_sub_similarity = get_subsequence_similarity(entity, col_name)
                name_cos_similarity = get_cos_similarity(entity_embedding, col_name_embeddings[cnum])
                comment_cos_similarity = get_cos_similarity(entity_embedding, comment_embeddings[cnum])
                column[8] = (name_sub_similarity,name_cos_similarity,comment_cos_similarity)
                # print(entity, col_name, (name_sub_similarity,name_cos_similarity,comment_cos_similarity))

            column_num_set = set()
            for column in sorted(schema, key=lambda x: x[8][0], reverse=True)[:4]:
                name_sub_similarity = column[8][0]
                if name_sub_similarity > threshold:
                    column_num_set.add(column[0])
            for column in sorted(schema, key=lambda x: x[8][1], reverse=True)[:4]:
                name_cos_similarity = column[8][1]
                if name_cos_similarity > threshold:
                    column_num_set.add(column[0])
            for column in sorted(schema, key=lambda x: x[8][2], reverse=True)[:4]:
                comment_cos_similarity = column[8][2]
                if comment_cos_similarity > threshold:
                    column_num_set.add(column[0])

            for enum, column in enumerate(schema,start=0):
                if enum in column_num_set:
                    column[9] = True
                    tbl_name = column[2]
                    tbl_name_selected.add(tbl_name)

    def get_related_value(
        self, 
        entity_list: list, 
        schema: list, 
        tbl_name_selected: set, 
        db_conn,
        use_lsh: bool = True,
        threshold: float = None
    ):
        if threshold is None:
            threshold = F_VAL_THRESHOLD
        cur = db_conn.cursor()
        for column in schema:
            col_type = column[4]
            if col_type.lower() == 'text':
                tbl_name = column[2]
                col_name = column[3]
                cur.execute(f"SELECT {col_name} FROM {tbl_name}")
                value_datas = cur.fetchall()
                value_list = [value_data[0] for value_data in value_datas]

                related_value_list = []
                if use_lsh:
                    query_results = lsh(entity_list,value_list)
                    if query_results != {}:
                        for entity, values in query_results.items():
                            embedding_list = get_embedding_list([entity] + values)
                            for enum, value in enumerate(values,start=1):
                                subsequence_similarity = get_subsequence_similarity(entity, value)
                                cos_similarity = get_cos_similarity(embedding_list[0], embedding_list[enum])
                                # print(entity, value, subsequence_similarity, cos_similarity)
                                if subsequence_similarity > threshold or cos_similarity > threshold:
                                    related_value_list.append(value)
                else:
                    entity_embeddings = get_embedding_list(entity_list)
                    value_embeddings = get_embedding_list(value_list)
                    for enum, entity in enumerate(entity_list,start=0):
                        for vnum, value in enumerate(value_list,start=0):
                            subsequence_similarity = get_subsequence_similarity(entity, value)
                            cos_similarity = get_cos_similarity(entity_embeddings[enum], value_embeddings[vnum])
                            # print(entity, value, subsequence_similarity, cos_similarity)
                            if subsequence_similarity > threshold or cos_similarity > threshold:
                                    related_value_list.append(value)
                # print(related_value_list)
                if len(related_value_list) != 0:
                    distinct_value_list = list(dict.fromkeys(related_value_list))
                    column_value_list = column[6]
                    if column_value_list is None:
                        column[6] = distinct_value_list
                    else:
                        column[6].extend(distinct_value_list)
                    column[9] = True
                    tbl_name_selected.add(tbl_name)

    def sel_pf_keys(
        self, 
        schema: list, 
        tbl_name_selected: set
    ):
        for column in schema:
            is_primary_key = column[1]
            tbl_name = column[2]
            fk = column[7]
            if (is_primary_key == 1 and tbl_name in tbl_name_selected) \
            or (fk is not None and tbl_name in tbl_name_selected):
                column[9] = True

    def get_schema_str(
        self, 
        schema: list, 
        tbl_name_selected: set, 
        need_type: bool = False
    ) -> str:
        def add_tbl_to_schema_str(tbl_name, schema_str):
            schema_str += "=====\n"
            schema_str += f"Table: {tbl_name}\nColumn:\n"
            return schema_str

        def add_col_to_schema_str(column, schema_str):
            col_name = column[3]
            comment = column[5]
            schema_str += "(" + col_name + "; " + "Comment: " + comment
            if need_type:
                col_type = column[4]
                schema_str += "; Type: " + col_type
            is_primary_key = column[1]
            sample = column[6]
            foreign_key = column[7]
            if sample is not None:
                schema_str += "; Sample: " + ", ".join(sample)
            if is_primary_key == 1:
                schema_str += "; Primary key"
            if foreign_key is not None and foreign_key[0] in tbl_name_selected:
                ref_tbl_name = foreign_key[0]
                ref_col_name = foreign_key[1]
                schema_str += "; Foreign key: references " + ref_tbl_name + "(" + ref_col_name + ")"
            schema_str += ")\n"
            return schema_str

        schema_str = ""
        tbl_now = None
        for column in schema:
            tbl_name = column[2]
            is_selected = column[9]
            if (tbl_now is None or tbl_now != tbl_name) and tbl_name in tbl_name_selected:
                schema_str = add_tbl_to_schema_str(tbl_name=tbl_name,schema_str=schema_str)
                tbl_now = tbl_name
            if is_selected:
                schema_str = add_col_to_schema_str(column=column,schema_str=schema_str)
        
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
        # print("="*10,"PROMPT","="*10)
        # print(prompt)
        return prompt

    @timeout(90)
    def get_filter_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        # print("="*10,"ANSWER","="*10)
        # print(answer)
        return answer

    def prune_schema(
        self,
        ans_json: dict,
        schema: list,
        tbl_name_selected: set
    ):
        for column in schema:
            column[9] = False
        tbl_name_selected.clear()

        for sel_tbl_name, sel_col_list in ans_json.items():
            if len(sel_col_list) != 0:
                tbl_name_selected.add(sel_tbl_name)
                for column in schema:
                    tbl_name = column[2]
                    col_name = column[3]
                    if tbl_name == sel_tbl_name and col_name in sel_col_list:
                        column[9] = True

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
            # print("The message is being processed by " + FILTER + "...")
            noun_list = self.parse_nouns(message['question'])
            tbl_name_selected = set()
            hint_list = self.get_related_hint_list(entity_list=message['entity'],vectordb=vectordb)
            hint_str, entity_list = self.process_hint_list(hint_list=hint_list, entity_list=message['entity'])
            schema = self.get_schema(db_conn=db_conn)
            self.add_fk_to_schema(schema=schema,db_conn=db_conn)
            self.get_related_column(
                entity_list=entity_list,schema=schema,tbl_name_selected=tbl_name_selected)
            self.get_related_column(
                entity_list=noun_list,schema=schema,tbl_name_selected=tbl_name_selected,threshold=0.35)
            self.get_related_value(
                entity_list=entity_list,schema=schema,tbl_name_selected=tbl_name_selected,db_conn=db_conn)
            self.get_related_value(
                entity_list=noun_list,schema=schema,tbl_name_selected=tbl_name_selected,db_conn=db_conn,use_lsh=False,threshold=0.35)
            self.sel_pf_keys(schema=schema, tbl_name_selected=tbl_name_selected)
            schema_str = self.get_schema_str(schema=schema, tbl_name_selected=tbl_name_selected, need_type=False)
            prompt = self.create_filter_prompt(schema_str=schema_str, hint_str=hint_str, question=message['question'])
            ans = self.get_filter_ans(prompt=prompt, llm=llm)
            ans_json = parse_json(ans)
            self.prune_schema(ans_json=ans_json, schema=schema, tbl_name_selected=tbl_name_selected)
            self.sel_pf_keys(schema=schema, tbl_name_selected=tbl_name_selected)
            new_schema_str = self.get_schema_str(schema=schema, tbl_name_selected=tbl_name_selected, need_type=True)
            message["schema"] = new_schema_str
            message["hint"] = hint_str
            message["message_to"] = GENERATOR
            return message