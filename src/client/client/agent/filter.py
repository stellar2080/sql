from llm.llm_base import LLM_Base
from utils.const import F_COL_STRONG_THRESHOLD, F_VAL_STRONG_THRESHOLD, FILTER, GENERATOR, F_HINT_THRESHOLD, F_COL_THRESHOLD, F_VAL_THRESHOLD
from utils.template import filter_template, filter_hint_template
from utils.utils import parse_json, user_message, get_response_content, timeout, \
    get_subsequence_similarity, get_embedding_list, get_cos_similarity, parse_list, lsh
from agent.agent_base import Agent_Base
from vectordb.vectordb import VectorDB
import spacy

class Filter(Agent_Base):
    def __init__(self, config):
        super().__init__()
        self.platform = config.get('platform','')
        self.user_id = config.get('user_id','')

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
        threshold: float = None,
    ) -> list:
        if threshold is None:
            threshold = F_HINT_THRESHOLD
        hint_list = []
        hint_ids = vectordb.get_related_key(
            user_id=self.user_id,
            query_texts=entity_list, 
            extracts=['distances', 'metadatas']
        )
        filtered_ids = None

        if len(entity_list) == 1:
            distances = hint_ids['distances']
            metadatas = hint_ids['metadatas']

            filtered_metadatas = [
                (1 - distance, metadata)
                for distance, metadata in zip(distances, metadatas)
                if 1 - distance > threshold
            ]

            filtered_metadatas.sort(key=lambda x: x[0], reverse=True)

            filtered_ids = [
                metadata['doc_id'] 
                for _, metadata in filtered_metadatas
            ]
            if filtered_ids:
                doc_list = vectordb.get_doc_by_id(
                    user_id=self.user_id,
                    embedding_ids=filtered_ids
                )
                hint_list.extend(doc_list)

        else:
            for i in range(len(entity_list)):
                distances = hint_ids['distances'][i]
                metadatas = hint_ids['metadatas'][i]

                filtered_metadatas = [
                    (1 - distance, metadata)
                    for distance, metadata in zip(distances, metadatas)
                    if 1 - distance > threshold
                ]
                
                filtered_metadatas.sort(key=lambda x: x[0], reverse=True)

                filtered_ids = [
                    metadata['doc_id'] 
                    for _, metadata in filtered_metadatas
                ]
                
                if filtered_ids:
                    doc_list = vectordb.get_doc_by_id(
                        user_id=self.user_id,
                        embedding_ids=filtered_ids
                    )
                    hint_list.extend(doc_list)

        distinct_hint_list = list(dict.fromkeys(hint_list))
        return distinct_hint_list

    def process_hint_list(
        self,
        hint_list: list,
        entity_list: list,
    ) -> tuple[str, list, list]:
        hint_str = ""
        proc_hint_list = []
        if hint_list:
            for enum, hint in enumerate(hint_list,start=1):
                express_list = parse_list(hint)
                expression = " ".join(express_list)
                proc_hint_list.append(expression)
                hint_str += f"[{enum}] " + expression + "\n"

                for entity in express_list:
                    if len(entity) > 1:
                        entity_list.append(entity)
            entity_list = list(dict.fromkeys(entity_list))
        return hint_str, entity_list, proc_hint_list

    def get_schema(
        self,
        db_conn
    ) -> tuple[list,dict,list,list,list]:
        cur = db_conn.cursor()
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        tbl_datas = cur.fetchall()

        schema = []
        schema_dict = {}
        tbl_name_list = []
        col_name_list = []
        comment_list = []

        for tbl_data in tbl_datas:
            tbl_name = tbl_data[0]
            sql_str = tbl_data[1]
            schema_dict[tbl_name] = {}
            tbl_name_list.append(tbl_name)
            
            cur.execute(f"PRAGMA table_info({tbl_name})")
            col_datas = cur.fetchall()
            columns = []
            for col_data in col_datas:
                is_primary_key = col_data[5]
                col_name = col_data[1]
                col_type = col_data[2]
                col_name_list.append(col_name)
                columns.append([tbl_name, col_name, col_type])
                schema_dict[tbl_name][col_name] = [is_primary_key, col_type]
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
                    comment_list.append(comment_str)
                    columns[num].extend([comment_str,None])
                    col_name = columns[num][1]
                    schema_dict[tbl_name][col_name].extend([comment_str,None,None,False])
                    num += 1
            schema.extend(columns)

        # schema [0 tbl_name,1 col_name,2 col_type,3 comment,4 similarity]
        # schema_dict [0 is_primary_key,1 col_type,2 comment,3 value_list, 4 fk,5 ischosen]
        return schema, schema_dict, tbl_name_list, col_name_list, comment_list

    def add_fk_to_schema(
        self,
        schema_dict: dict,
        tbl_name_list: list,
        db_conn
    ):
        cur = db_conn.cursor()
        for tbl_name in tbl_name_list:
            cur.execute(f"PRAGMA foreign_key_list({tbl_name})")
            fk_datas = cur.fetchall()
            for fk_data in fk_datas:
                fk_col_name = fk_data[3]
                ref_tbl_name = fk_data[2]
                ref_col_name = fk_data[4]
                schema_dict[tbl_name][fk_col_name][4] = (ref_tbl_name, ref_col_name)

    def get_related_column(
        self, 
        entity_list: list,
        noun_list: list, 
        schema: list, 
        schema_dict: dict,
        col_name_list: list,
        comment_list: list,
        tbl_name_selected: set,
        threshold: float = None
    ) -> set:
        if threshold is None:
            threshold = F_COL_THRESHOLD

        entitys_length = len(entity_list)
        nouns_length = len(noun_list)
        cols_length = len(col_name_list)
        embeddings = get_embedding_list(entity_list + noun_list + col_name_list + comment_list)
        entity_embeddings = embeddings[:entitys_length]
        noun_embeddings = embeddings[entitys_length:entitys_length+nouns_length]
        col_name_embeddings = embeddings[entitys_length+nouns_length:entitys_length+nouns_length+cols_length]
        comment_embeddings = embeddings[entitys_length+nouns_length+cols_length:]
        
        strong_rela_set = set()
        for enum, entity in enumerate(entity_list, start=0):
            entity_embedding = entity_embeddings[enum]
            for cnum, column in enumerate(schema, start=0):
                col_name = column[1]
                name_sub_similarity = get_subsequence_similarity(entity, col_name)
                name_cos_similarity = get_cos_similarity(entity_embedding, col_name_embeddings[cnum])
                comment_cos_similarity = get_cos_similarity(entity_embedding, comment_embeddings[cnum])
                column[4] = (name_sub_similarity,name_cos_similarity,comment_cos_similarity)
                # print(entity, col_name, (name_sub_similarity,name_cos_similarity,comment_cos_similarity))

            filtered_schema = [
                column for column in schema
                if column[4][0] > threshold or column[4][1] > threshold or column[4][2] > threshold
            ]
            
            sort_schema = sorted(
                filtered_schema,
                key=lambda x: max(x[4][0], x[4][1], x[4][2]),
                reverse=True
            )[:10]

            for column in sort_schema:
                name_sub_similarity = column[4][0]
                name_cos_similarity = column[4][1]
                comment_cos_similarity = column[4][2]
                tbl_name = column[0]   
                col_name = column[1]

                if name_sub_similarity > threshold:
                    schema_dict[tbl_name][col_name][5] = True
                    tbl_name_selected.add(tbl_name)
                    if name_sub_similarity > F_COL_STRONG_THRESHOLD:
                        # print(col_name, name_cos_similarity)
                        strong_rela_set.add((tbl_name,col_name))

                if name_cos_similarity > threshold:
                    schema_dict[tbl_name][col_name][5] = True
                    tbl_name_selected.add(tbl_name)
                    if name_cos_similarity > F_COL_STRONG_THRESHOLD:
                        # print(col_name, name_cos_similarity)
                        strong_rela_set.add((tbl_name,col_name))

                if comment_cos_similarity > threshold:
                    schema_dict[tbl_name][col_name][5] = True
                    tbl_name_selected.add(tbl_name)
                    if comment_cos_similarity > F_COL_STRONG_THRESHOLD:
                        strong_rela_set.add((tbl_name,col_name))

        if noun_list:
            low_threshold = threshold - 0.25
            for enum, noun in enumerate(noun_list, start=0):
                noun_embedding = noun_embeddings[enum]
                for cnum, column in enumerate(schema, start=0):
                    col_name = column[1]
                    name_sub_similarity = get_subsequence_similarity(noun, col_name)
                    name_cos_similarity = get_cos_similarity(noun_embedding, col_name_embeddings[cnum])
                    comment_cos_similarity = get_cos_similarity(noun_embedding, comment_embeddings[cnum])
                    column[4] = (name_sub_similarity,name_cos_similarity,comment_cos_similarity)
                    # print(noun, col_name, (name_sub_similarity,name_cos_similarity,comment_cos_similarity))

                filtered_schema = [
                    column for column in schema
                    if column[4][0] > low_threshold or column[4][1] > low_threshold or column[4][2] > low_threshold
                ]
                
                if filtered_schema:
                    sort_schema = sorted(
                        filtered_schema,
                        key=lambda x: max(x[4][0], x[4][1], x[4][2]),
                        reverse=True
                    )[:10]

                    for column in sort_schema:
                        name_sub_similarity = column[4][0]
                        name_cos_similarity = column[4][1]
                        comment_cos_similarity = column[4][2]
                        tbl_name = column[0]   
                        col_name = column[1]

                        if name_sub_similarity > low_threshold:
                            schema_dict[tbl_name][col_name][5] = True
                            tbl_name_selected.add(tbl_name)
                            if name_sub_similarity > F_COL_STRONG_THRESHOLD:
                                # print(col_name, name_cos_similarity)
                                strong_rela_set.add((tbl_name,col_name))

                        if name_cos_similarity > low_threshold:
                            schema_dict[tbl_name][col_name][5] = True
                            tbl_name_selected.add(tbl_name)
                            if name_cos_similarity > F_COL_STRONG_THRESHOLD:
                                # print(col_name, name_cos_similarity)
                                strong_rela_set.add((tbl_name,col_name))

                        if comment_cos_similarity > low_threshold:
                            schema_dict[tbl_name][col_name][5] = True
                            tbl_name_selected.add(tbl_name)
                            if comment_cos_similarity > F_COL_STRONG_THRESHOLD:
                                strong_rela_set.add((tbl_name,col_name))

        return strong_rela_set


    def get_related_value(
        self, 
        entity_list: list, 
        noun_list: list,
        schema_dict: dict,
        tbl_name_selected: set, 
        db_conn,
        threshold: float = None
    ) -> set:
        if threshold is None:
            threshold = F_VAL_THRESHOLD
        strong_rela_set = set()
        cur = db_conn.cursor()

        for tbl_name, col_datas in schema_dict.items():
            for col_name, col_data in col_datas.items():
                col_type = col_data[1]
            if col_type.lower() == 'text':
                cur.execute(f"SELECT {col_name} FROM {tbl_name}")
                value_datas = cur.fetchall()
                value_list = [value_data[0] for value_data in value_datas]

                related_value_list = []
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
                                if subsequence_similarity > F_VAL_STRONG_THRESHOLD or cos_similarity > F_VAL_STRONG_THRESHOLD:
                                    strong_rela_set.add((tbl_name,col_name))
                if noun_list:
                    low_threshold = threshold - 0.25
                    noun_length = len(noun_list)
                    embeddings = get_embedding_list(noun_list + value_list)
                    noun_embeddings = embeddings[:noun_length]
                    value_embeddings = embeddings[noun_length:]
                    for enum, noun in enumerate(noun_list,start=0):
                        for vnum, value in enumerate(value_list,start=0):
                            subsequence_similarity = get_subsequence_similarity(noun, value)
                            cos_similarity = get_cos_similarity(noun_embeddings[enum], value_embeddings[vnum])
                            # print(noun, value, subsequence_similarity, cos_similarity)
                            if subsequence_similarity > low_threshold or cos_similarity > low_threshold:
                                related_value_list.append(value)
                                if subsequence_similarity > F_VAL_STRONG_THRESHOLD or cos_similarity > F_VAL_STRONG_THRESHOLD:
                                    strong_rela_set.add((tbl_name,col_name))
                # print(related_value_list)
                if len(related_value_list) != 0:
                    distinct_value_list = list(dict.fromkeys(related_value_list))
                    column_value_list = schema_dict[tbl_name][col_name][3]
                    if column_value_list is None:
                        schema_dict[tbl_name][col_name][3] = distinct_value_list
                    else:
                        schema_dict[tbl_name][col_name][3].extend(distinct_value_list)
                    schema_dict[tbl_name][col_name][5] = True
                    tbl_name_selected.add(tbl_name)

        return strong_rela_set
    
    def get_schema_str(
        self, 
        schema_dict: dict, 
        tbl_name_selected: set, 
        need_type: bool = False
    ) -> str:
        def add_tbl_to_schema_str(tbl_name, schema_str):
            schema_str += "=====\n"
            schema_str += f"Table: {tbl_name}\nColumn:\n"
            return schema_str

        def add_col_to_schema_str(col_name, col_data, schema_str):
            comment = col_data[2]
            schema_str += "(" + col_name + "; " + "Comment: " + comment
            if need_type:
                col_type = col_data[1]
                schema_str += "; Type: " + col_type
            is_primary_key = col_data[0]
            sample = col_data[3]
            foreign_key = col_data[4]
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
        for tbl_name, col_datas in schema_dict.items():
            add_tbl_flag = True
            for col_name, col_data in col_datas.items():
                is_selected = col_data[5]
                if is_selected:
                    if add_tbl_flag:
                        schema_str = add_tbl_to_schema_str(tbl_name=tbl_name,schema_str=schema_str)
                        add_tbl_flag = False
                    schema_str = add_col_to_schema_str(col_name=col_name,col_data=col_data,schema_str=schema_str)
        
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

    @timeout(90)
    def get_filter_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        llm_message = [user_message(prompt)]
        response = llm.call(messages=llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        print("="*10,"ANSWER","="*10)
        print(answer)
        return answer

    def prune_schema(
        self,
        ans_json: dict,
        schema_dict: dict,
        tbl_name_selected: set
    ):
        for tbl_name, col_datas in schema_dict.items():
            for col_name, col_data in col_datas.items():
                col_data[5] = False
        tbl_name_selected.clear()

        for sel_tbl_name, sel_col_list in ans_json.items():
            if len(sel_col_list) != 0:
                tbl_name_selected.add(sel_tbl_name)
                for sel_col_name in sel_col_list:
                    schema_dict[sel_tbl_name][sel_col_name][5] = True

    def add_strong_rela_column(
        self,
        schema_dict: dict,
        strong_rela_set: set,
        tbl_name_selected: set
    ):
        for tbl_name, col_name in strong_rela_set:
            tbl_name_selected.add(tbl_name)
            schema_dict[tbl_name][col_name][5] = True

    def sel_pf_keys(
        self, 
        schema_dict: dict,
        tbl_name_selected: set
    ):
        for tbl_name, col_datas in schema_dict.items():
            for col_name, col_data in col_datas.items():
                is_primary_key = col_data[0]
                fk = col_data[4]
                if (is_primary_key == 1 and tbl_name in tbl_name_selected) \
                or (fk is not None and tbl_name in tbl_name_selected):
                    col_data[5] = True

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
            print(hint_list)
            hint_str, entity_list, proc_hint_list = self.process_hint_list(hint_list=hint_list, entity_list=message['entity'])
            schema, schema_dict, tbl_name_list, col_name_list, comment_list = self.get_schema(db_conn=db_conn)
            self.add_fk_to_schema(schema_dict=schema_dict,tbl_name_list=tbl_name_list,db_conn=db_conn)
            strong_rela_set_p1 = self.get_related_column(
                entity_list=entity_list,noun_list=noun_list,schema=schema,schema_dict=schema_dict,col_name_list=col_name_list,comment_list=comment_list,tbl_name_selected=tbl_name_selected)
            strong_rela_set_p2 = self.get_related_value(
                entity_list=entity_list,noun_list=noun_list,schema_dict=schema_dict,tbl_name_selected=tbl_name_selected,db_conn=db_conn)
            strong_rela_set = strong_rela_set_p1 | strong_rela_set_p2
            self.sel_pf_keys(schema_dict=schema_dict, tbl_name_selected=tbl_name_selected)
            schema_str = self.get_schema_str(schema_dict=schema_dict, tbl_name_selected=tbl_name_selected, need_type=False)
            prompt = self.create_filter_prompt(schema_str=schema_str, hint_str=hint_str, question=message['question'])
            ans = self.get_filter_ans(prompt=prompt, llm=llm)
            ans_json = parse_json(ans)
            self.prune_schema(ans_json=ans_json, schema_dict=schema_dict, tbl_name_selected=tbl_name_selected)
            self.add_strong_rela_column(schema_dict=schema_dict, strong_rela_set=strong_rela_set, tbl_name_selected=tbl_name_selected)
            self.sel_pf_keys(schema_dict=schema_dict, tbl_name_selected=tbl_name_selected)
            new_schema_str = self.get_schema_str(schema_dict=schema_dict, tbl_name_selected=tbl_name_selected, need_type=True)
            print(strong_rela_set)
            print(new_schema_str)
            message["schema"] = new_schema_str
            message["hint"] = proc_hint_list
            message["message_to"] = GENERATOR
            return message