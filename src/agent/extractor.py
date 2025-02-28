from src.llm.llm_base import LLM_Base
from src.utils.const import E_HINT_THRESHOLD, E_COL_THRESHOLD, E_COL_STRONG_THRESHOLD, E_VAL_THRESHOLD, E_VAL_STRONG_THRESHOLD, EXTRACTOR, FILTER
from src.utils.template import extractor_template, extractor_hint_template
from src.utils.utils import get_cos_similarity, get_embedding, get_embedding_list, user_message, get_response_content, timeout, parse_list
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB

class Extractor(Agent_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self.platform = config['platform']

    def get_rela_hint_keys(
        self,
        question: str,
        vectordb: VectorDB,
    ) -> set:
        hint_keys = vectordb.get_related_key(query_texts=question, extracts=['distances', 'documents'])
        distances = hint_keys['distances']
        documents = hint_keys['documents']
        hint_key_list = [
            document for distance, document in sorted(
                zip(distances, documents), key=lambda x: x[0]
            ) if 1 - distance > E_HINT_THRESHOLD
        ]
        hint_key_set = set(hint_key_list)
        return hint_key_set

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

        for enum, tbl_name in enumerate(tbl_names,start=0):
            cur.execute(f"PRAGMA table_info({tbl_name})")
            col_datas = cur.fetchall()
            columns = []
            for col_data in col_datas:
                col_name = col_data[1]
                col_type = col_data[2]
                columns.append([tbl_name, col_name, col_type])

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
                    columns[num].extend([comment_str,None])
                    num += 1
            schema.extend(columns)

        # schema = [[0 tbl_name,1 col_name,2 col_type,3 comment,4 similarity],...]
        return schema

    def get_related_column(
        self,
        question: str,
        schema
    ) -> tuple[set,set]:
        column_set = set()
        strong_rala_set = set()

        col_name_list = []
        comment_list = []
        for column in schema:
            col_name = column[1]
            comment = column[3]
            col_name_list.append(col_name)
            comment_list.append(comment)
        question_embedding = get_embedding(question)
        col_name_embeddings = get_embedding_list(col_name_list)
        comment_embeddings = get_embedding_list(comment_list)

        for enum, column in enumerate(schema, start=0):
            name_cos_similarity = get_cos_similarity(question_embedding, col_name_embeddings[enum])
            comment_cos_similarity = get_cos_similarity(question_embedding, comment_embeddings[enum])
            column[4] = (name_cos_similarity,comment_cos_similarity)
            # print(column[1], (name_cos_similarity,comment_cos_similarity))

        sort_schema = sorted(schema, key=lambda x: x[4][0], reverse=True)[:10]
        for enum, column in enumerate(sort_schema, start=0):
            name_cos_similarity = column[4][0]
            col_name = column[1]       
            if name_cos_similarity > E_COL_THRESHOLD:
                column_set.add(col_name)
                if name_cos_similarity > E_COL_STRONG_THRESHOLD:
                    # print(col_name, name_cos_similarity)
                    strong_rala_set.add(col_name)
                
        sort_schema = sorted(schema, key=lambda x: x[4][1], reverse=True)[:10]
        for enum, column in enumerate(sort_schema, start=0):
            comment_cos_similarity = column[4][1]
            comment = column[3]
            if comment_cos_similarity > E_COL_THRESHOLD:
                column_set.add(comment)
                if comment_cos_similarity > E_COL_STRONG_THRESHOLD:
                    # print(comment, comment_cos_similarity)
                    strong_rala_set.add(comment)

        # print(strong_rala_set)
        return column_set, strong_rala_set

    def get_related_value(
        self, 
        question: str,
        schema: list,
        db_conn
    ) -> tuple[set,set]:
        value_set = set()
        strong_rala_set = set()
        cur = db_conn.cursor()
        for column in schema:
            tbl_name = column[0]
            col_name = column[1]
            col_type = column[2]
            if col_type.lower() == 'text':
                cur.execute(f"SELECT {col_name} FROM {tbl_name}")
                value_datas = cur.fetchall()
                value_list = [value_data[0] for value_data in value_datas]

                question_embedding = get_embedding(question)
                value_embeddings = get_embedding_list(value_list)
                for enum, value in enumerate(value_list, start=0):
                    cos_similarity = get_cos_similarity(vec1=question_embedding, vec2=value_embeddings[enum])
                    if cos_similarity > E_VAL_THRESHOLD:
                        value_set.add(value)
                        if cos_similarity > E_VAL_STRONG_THRESHOLD:
                            strong_rala_set.add(value)

        return value_set, strong_rala_set

    def get_hint_str(
        self,
        entity_set
    ) -> str:
        hint_str = ""
        if len(entity_set) == 0:
            return hint_str
        hint_str += "{"
        entity_list = list(entity_set)
        length = len(entity_list)
        for idx in range(length):
            entity = entity_list[idx]
            hint_str += '"' + entity + '"'
            if idx != length - 1:
                hint_str += ", "
        hint_str += "}"
        return hint_str

    def create_extractor_prompt(
        self,
        question: str,
        hint_str: set
    ) -> str:
        if len(hint_str) == "":
            prompt = extractor_template.format(question)
        else:
            prompt = extractor_template.format(question) + extractor_hint_template.format(hint_str)
        print("="*10,"PROMPT","="*10)
        print(prompt)
        return prompt

    @timeout(90)
    def get_extractor_ans(
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

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None,
        db_conn = None
    ):
        if message["message_to"] != EXTRACTOR:
            raise Exception("The message should not be processed by " + EXTRACTOR + 
                            ". It is sent to " + message["message_to"])
        else:
            # print("The message is being processed by " + EXTRACTOR + "...")
            schema = self.get_schema(db_conn=db_conn)
            hint_set = self.get_rela_hint_keys(question=message['question'], vectordb=vectordb)
            col_set, strong_rela_col_set = self.get_related_column(question=message['question'], schema=schema)
            value_set, strong_rela_value_set = self.get_related_value(question=message['question'], schema=schema, db_conn=db_conn)
            entity_set = hint_set | col_set | value_set
            strong_rela_set = strong_rela_col_set | strong_rela_value_set
            strong_rela_list = list(strong_rela_set)
            print(strong_rela_list)
            hint_str = self.get_hint_str(entity_set=entity_set)
            prompt = self.create_extractor_prompt(question=message["question"], hint_str=hint_str)
            ans = self.get_extractor_ans(prompt=prompt, llm=llm)
            ans_list = parse_list(text=ans)
            ans_list.extend(strong_rela_list)
            distinct_ans_list = list(dict.fromkeys(ans_list))
            message["entity"] = distinct_ans_list
            message["message_to"] = FILTER
            return message
