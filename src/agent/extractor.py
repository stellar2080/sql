from src.llm.llm_base import LLM_Base
from src.utils.const import E_HINT_THRESHOLD, E_COL_THRESHOLD, E_VAL_THRESHOLD, EXTRACTOR, FILTER
from src.utils.template import extractor_template, extractor_hint_template
from src.utils.utils import get_cos_similarity, get_embedding, get_embedding_list, user_message, get_response_content, timeout, parse_list
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB
from src.utils.database_utils import connect_to_sqlite

class Extractor(Agent_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self.platform = config['platform']
        self.url = config.get("db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.conn, _ = connect_to_sqlite(self.url, self.check_same_thread)

    def get_rela_hint_keys(
        self,
        question: str,
        vectordb: VectorDB,
    ):
        hint_keys = vectordb.get_related_key(question, extracts=['distances', 'documents'])
        
        distances = hint_keys['distances']
        documents = hint_keys['documents']
        hint_key_list = [
            document for distance, document in sorted(
                zip(distances, documents), key=lambda x: x[0]
            ) if 1 - distance > E_HINT_THRESHOLD
        ]

        return set(hint_key_list)

    def get_schema(
        self
    ):
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
            cols = [[tbl_name, col_data[1],col_data[2]] for col_data in col_datas]

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

        # schema = [[0 tbl_name,1 col_name,2 col_type,3 comment,4 similarity],...]
        return schema

    def get_related_column(
        self,
        question: str,
        schema
    ):
        col_set = set()

        name_list = []
        comment_list = []
        for col in schema:
            name_list.append(col[1])
            comment_list.append(col[3])

        name_embeddings = get_embedding_list(name_list)
        comment_embeddings = get_embedding_list(comment_list)
        question_embedding = get_embedding(question)

        for enum, col in enumerate(schema, start=0):
            name_cos_similarity = get_cos_similarity(question_embedding, name_embeddings[enum])
            comment_cos_similarity = get_cos_similarity(question_embedding, comment_embeddings[enum])
            col[4] = (name_cos_similarity,comment_cos_similarity)
            # print(col[1], (name_cos_similarity,comment_cos_similarity))

        # print("=" * 30,"cos_similarity-col_name")
        for item in sorted(schema, key=lambda x: x[4][0], reverse=True)[:10]:
            # print(item)
            if item[4][0] > E_COL_THRESHOLD:
                col_set.add(item[1])
        # print("=" * 30,"cos_similarity-comment")
        for item in sorted(schema, key=lambda x: x[4][1], reverse=True)[:10]:
            # print(item)
            if item[4][1] > E_COL_THRESHOLD:
                col_set.add(item[3])

        return col_set

    def get_related_value(
        self, 
        question: str,
        schema: list,
    ):
        value_set = set()
        cur = self.conn.cursor()
        for col in schema:
            if col[2].lower() == 'text':
                cur.execute(f"SELECT {col[1]} FROM {col[0]}")
                value_list = [item[0] for item in cur.fetchall()]

                question_embedding = get_embedding(question)
                value_embeddings = get_embedding_list(value_list)
                for vnum, value in enumerate(value_list, start=0):
                    if get_cos_similarity(question_embedding, value_embeddings[vnum]) > E_VAL_THRESHOLD:
                            value_set.add(value)

        return value_set

    def create_extractor_prompt(
        self,
        question: str,
        entity_set: set
    ) -> str:
        if len(entity_set) == 0:
            prompt = extractor_template.format(question)
        else:
            prompt = extractor_template.format(question) + extractor_hint_template.format(entity_set)
        print("="*10,"PROMPT","="*10)
        print(prompt)
        return prompt

    @timeout(180)
    def get_extractor_ans(
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

    def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None
    ):
        if message["message_to"] != EXTRACTOR:
            raise Exception("The message should not be processed by " + EXTRACTOR + ". It is sent to " + message["message_to"])
        else:
            # print("The message is being processed by " + EXTRACTOR + "...")
            
            schema = self.get_schema()
            hint_set = self.get_rela_hint_keys(question=message['question'], vectordb=vectordb)
            col_set = self.get_related_column(question=message['question'], schema=schema)
            value_set = self.get_related_value(question=message['question'], schema=schema)
            entity_set = hint_set | col_set | value_set
            print("="*10,"entity_set")
            print(entity_set)

            prompt = self.create_extractor_prompt(message["question"], entity_set)
            ans = self.get_extractor_ans(prompt, llm)
            ans_list = parse_list(ans)
            
            message["entity"] = ans_list
            message["message_to"] = FILTER
            return message
