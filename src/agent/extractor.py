from src.llm.llm_base import LLM_Base
from src.utils.const import HINT_THRESHOLD, COL_THRESHOLD, VAL_THRESHOLD, EXTRACTOR, FILTER
from src.utils.template import extractor_template
from src.utils.utils import get_cos_similarity, get_embedding_list, get_subsequence_similarity, lsh, user_message, get_response_content, timeout, parse_list
from src.agent.agent_base import Agent_Base
from src.vectordb.vectordb import VectorDB

from src.utils.database_utils import connect_to_sqlite

import spacy

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

    def noun_chunking(
        self,
        question: str,
    ):
        ignore_texts = ['what','i']
        nlp = spacy.load('en_core_web_trf')
        doc = nlp(question)
        noun_chunks = []
        for chunk in doc.noun_chunks:
            text = chunk.text
            if text.lower() not in ignore_texts:
                noun_chunks.append(text)
        return noun_chunks

    def get_rela_hint_keys(
        self,
        entity_list: list,
        vectordb: VectorDB,
    ):
        hint_key_list = []

        hint_keys = vectordb.get_related_key(entity_list, extracts=['distances', 'documents'])
        for i in range(len(entity_list)):
            if len(entity_list) == 1:
                distances = hint_keys['distances']
                documents = hint_keys['documents']
            else:
                distances = hint_keys['distances'][i]
                documents = hint_keys['documents'][i]
            filtered_keys = [
                document for distance, document in sorted(
                    zip(distances, documents), key=lambda x: x[0]
                ) if distance < HINT_THRESHOLD
            ]
            # print(filtered_keys)
            if len(filtered_keys) != 0:
                hint_key_list.extend(filtered_keys)

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
        entity_list: list,
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
        noun_chunk_embeddings = get_embedding_list(entity_list)

        for e_idx, noun_chunk in enumerate(entity_list, start=0):
            noun_chunk_embedding = noun_chunk_embeddings[e_idx]
            for c_idx, col in enumerate(schema, start=0):
                col_name = col[1]
                name_sub_similarity = get_subsequence_similarity(noun_chunk, col_name)
                name_cos_similarity = get_cos_similarity(noun_chunk_embedding, name_embeddings[c_idx])
                comment_cos_similarity = get_cos_similarity(noun_chunk_embedding, comment_embeddings[c_idx])
                col[4] = (name_sub_similarity,name_cos_similarity,comment_cos_similarity)
                # print(noun_chunk, col_name, (name_sub_similarity,name_cos_similarity,comment_cos_similarity))

            # print("=" * 20)
            # print(noun_chunk)
            # print("="*30,"subsequence_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[4][0], reverse=True)[:4]:
                # print(item)
                if item[4][0] > COL_THRESHOLD:
                    col_set.add(item[1])
            # print("=" * 30,"cos_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[4][1], reverse=True)[:4]:
                # print(item)
                if item[4][1] > COL_THRESHOLD:
                    col_set.add(item[1])
            # print("=" * 30,"cos_similarity-comment")
            for item in sorted(schema, key=lambda x: x[4][2], reverse=True)[:4]:
                # print(item)
                if item[4][2] > COL_THRESHOLD:
                    col_set.add(item[3])

        return col_set

    def get_related_value(
        self, 
        entity_list: list,
        schema: list,
        use_lsh: bool = True
    ):
        value_set = set()
        cur = self.conn.cursor()
        for col in schema:
            if col[2].lower() == 'text':
                cur.execute(f"SELECT {col[1]} FROM {col[0]}")
                value_list = [item[0] for item in cur.fetchall()]

                if use_lsh:
                    query_results = lsh(entity_list,value_list)
                    if query_results != {}:
                        # print(query_results)
                        for key, values in query_results.items():
                            embedding_list = get_embedding_list([key] + values)
                            for vnum, value in enumerate(values,start=1):
                                # print(key, value, get_subsequence_similarity(key, value), get_cos_similarity(embedding_list[0], embedding_list[idx]))
                                if get_subsequence_similarity(key, value) > VAL_THRESHOLD \
                                or get_cos_similarity(embedding_list[0], embedding_list[vnum]) > VAL_THRESHOLD:
                                    value_set.add(value)
                else:
                    eneity_embeddings = get_embedding_list(entity_list)
                    value_embeddings = get_embedding_list(value_list)
                    for enum, entity in enumerate(entity_list, start=0):
                        for vnum, value in enumerate(value_list, start=0):
                            if get_subsequence_similarity(entity, value) > VAL_THRESHOLD \
                                or get_cos_similarity(eneity_embeddings[enum], value_embeddings[vnum]) > VAL_THRESHOLD:
                                    value_set.add(value)

        return value_set

    def create_extractor_prompt(
        self,
        question: str,
        entity_set: set
    ) -> (str,str):
        prompt = extractor_template.format(question, entity_set)
        print("="*10,"PROMPT","="*10)
        print(prompt)
        return prompt

    @timeout(180)
    def get_extractor_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> (dict, str):
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
            noun_chunks = self.noun_chunking(message['question'])
            print("="*10,"noun_chunks")
            print(noun_chunks)
            
            schema = self.get_schema()
            hint_set = self.get_rela_hint_keys(entity_list=noun_chunks + [message['question']], vectordb=vectordb)
            col_set = self.get_related_column(entity_list=noun_chunks + [message['question']],schema=schema)
            value_set = self.get_related_value(entity_list=noun_chunks, schema=schema, use_lsh=True)
            value_set_2 = self.get_related_value(entity_list=[message['question']], schema=schema, use_lsh=False)
            entity_set = hint_set | col_set | value_set | value_set_2
            print("="*10,"entity_set")
            print(entity_set)

            prompt = self.create_extractor_prompt(message["question"], entity_set)
            ans = self.get_extractor_ans(prompt, llm)
            ans_list = parse_list(ans)
            
            entity_set.update(noun_chunks)
            entity_set.update(ans_list)
            entity_list = list(entity_set)
            print("="*10,"entity_list")
            print(entity_list)
            message["entity"] = entity_list
            message["message_to"] = FILTER
            return message
