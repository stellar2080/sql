from src.llm.llm_base import LLM_Base
from src.utils.const import COL_THRESHOLD, EVIDENCE_THRESHOLD, EXTRACTOR, EXTRACTOR_COL_THRESHOLD, EXTRACTOR_VAL_THRESHOLD, FILTER, VAL_THRESHOLD
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
        nlp = spacy.load('en_core_web_trf')
        doc = nlp(question)
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        return noun_chunks

    def get_rela_evidence_keys(
        self,
        noun_chunks: list,
        vectordb: VectorDB,
    ):
        return_list = []

        evidence_keys = vectordb.get_related_key(noun_chunks, extracts=['distances', 'documents'])
        for i in range(len(noun_chunks)):
            if len(noun_chunks) == 1:
                distances = evidence_keys['distances']
                documents = evidence_keys['documents']
            else:
                distances = evidence_keys['distances'][i]
                documents = evidence_keys['documents'][i]
            filtered_keys = [
                document for distance, document in sorted(
                    zip(distances, documents), key=lambda x: x[0]
                ) if distance < EVIDENCE_THRESHOLD
            ]
            # print(filtered_keys)
            if len(filtered_keys) != 0:
                return_list.extend(filtered_keys)

        return set(return_list)

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

        # schema = [[tbl_name,col_name,col_type,comment,similarity],...]
        return schema

    def get_related_column(
        self,
        noun_chunks: list,
        schema
    ):
        col_set = set()

        name_embeddings = get_embedding_list([col[1].lower().replace('_',' ').replace('-',' ') for col in schema])
        comment_embeddings = get_embedding_list([col[3].lower().replace('_',' ').replace('-',' ') for col in schema])
        noun_chunk_embeddings = get_embedding_list([noun_chunk.lower().replace('_',' ').replace('-',' ') for noun_chunk in noun_chunks])

        for e_idx, noun_chunk in enumerate(noun_chunks, start=0):
            noun_chunk_embedding = noun_chunk_embeddings[e_idx]
            for c_idx, col in enumerate(schema, start=0):
                col_name = col[1]
                s_similarity = get_subsequence_similarity(noun_chunk, col_name)
                name_cos_similarity = get_cos_similarity(noun_chunk_embedding, name_embeddings[c_idx])
                comment_cos_similarity = get_cos_similarity(noun_chunk_embedding, comment_embeddings[c_idx])
                col[4] = (s_similarity,name_cos_similarity,comment_cos_similarity)
                # print(noun_chunk, col_name, (s_similarity,name_cos_similarity,comment_cos_similarity))

            # print("=" * 20)
            # print(noun_chunk)
            # print("="*30,"subsequence_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[4][0], reverse=True)[:4]:
                # print(item)
                if item[4][0] > EXTRACTOR_COL_THRESHOLD:
                    col_set.add(item[1])
            # print("=" * 30,"cos_similarity-col_name")
            for item in sorted(schema, key=lambda x: x[4][1], reverse=True)[:4]:
                # print(item)
                if item[4][1] > EXTRACTOR_COL_THRESHOLD:
                    col_set.add(item[1])
            # print("=" * 30,"cos_similarity-comment")
            for item in sorted(schema, key=lambda x: x[4][2], reverse=True)[:4]:
                # print(item)
                if item[4][2] > EXTRACTOR_COL_THRESHOLD:
                    col_set.add(item[3])

        return col_set

    def get_related_value(
        self, 
        noun_chunks: list,
        schema: list
    ):
        value_set = set()
        cur = self.conn.cursor()
        for item in schema:
            if item[2].lower() == 'text':
                cur.execute(f"SELECT {item[1]} FROM {item[0]}")
                value_list = [item[0] for item in cur.fetchall()]

                query_results = lsh(noun_chunks,value_list)
                if query_results != {}:
                    # print(query_results)
                    for key, values in query_results.items():
                        embedding_list = get_embedding_list([key] + values)
                        for idx, value in enumerate(values,start=1):
                            # print(key, value, get_subsequence_similarity(key, value), get_cos_similarity(embedding_list[0], embedding_list[idx]))
                            if get_subsequence_similarity(key, value) > EXTRACTOR_VAL_THRESHOLD \
                            or get_cos_similarity(embedding_list[0], embedding_list[idx]) > EXTRACTOR_VAL_THRESHOLD:
                                value_set.add(value)

        return value_set

    def create_extractor_prompt(
        self,
        question: str,
        entity_set: set
    ) -> (str,str):
        prompt = extractor_template.format(question, entity_set)
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
            evidence_set = self.get_rela_evidence_keys(noun_chunks=noun_chunks, vectordb=vectordb)
            schema = self.get_schema()
            col_set = self.get_related_column(noun_chunks=noun_chunks,schema=schema)
            value_set = self.get_related_value(noun_chunks=noun_chunks, schema=schema)
            entity_set = col_set | value_set | evidence_set
            prompt = self.create_extractor_prompt(message["question"], entity_set)

            ans = self.get_extractor_ans(prompt, llm)
            entity_list = parse_list(ans)

            message["extract"] = [entity.lower().replace('_',' ').replace('-',' ') for entity in entity_list]
            message["message_to"] = FILTER
            return message
