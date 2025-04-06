import aiosqlite
from client.llm.llm_base import LLM_Base
from client.utils.const import EXTRACTOR, FILTER
from client.utils.template import extractor_template, extractor_hint_template
from client.utils.utils import get_cos_similarity, get_embedding_list, user_message, get_response_content, timeout, parse_list
from client.agent.agent_base import Agent_Base
from client.vectordb.vectordb import VectorDB

class Extractor(Agent_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self.platform = config.get('platform')
        self.target_db_url = config.get("target_db_url")
        self.E_HINT_THRESHOLD = config.get('E_HINT_THRESHOLD')
        self.E_COL_THRESHOLD = config.get('E_COL_THRESHOLD')
        self.E_VAL_THRESHOLD = config.get('E_VAL_THRESHOLD')
        self.E_COL_STRONG_THRESHOLD = config.get('E_COL_STRONG_THRESHOLD')
        self.E_VAL_STRONG_THRESHOLD = config.get('E_VAL_STRONG_THRESHOLD')

    async def get_rela_hint_keys(
        self,
        question: str,
        vectordb: VectorDB,
    ) -> set:
        hint_keys = await vectordb.get_related_key(query_texts=question, extracts=['distances', 'documents'])
        distances = hint_keys['distances']
        documents = hint_keys['documents']

        filtered_keys = [
            (1 - distance, document)
            for distance, document in zip(distances, documents)
            if 1 - distance > self.E_HINT_THRESHOLD
        ]
        filtered_keys.sort(key=lambda x: x[0], reverse=True)
        hint_key_list = [
            document 
            for _, document in filtered_keys
        ]
        hint_key_set = set(hint_key_list)
        return hint_key_set

    async def get_schema(
        self,
    ) -> tuple[list,list,list]:
        async with aiosqlite.connect(self.target_db_url) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
            tbl_datas = await cursor.fetchall()

            schema = []
            col_name_list = []
            comment_list = []

            for tbl_data in tbl_datas:
                tbl_name = tbl_data[0]
                sql_str = tbl_data[1]
                await cursor.execute(f"PRAGMA table_info({tbl_name})")
                col_datas = await cursor.fetchall()
                columns = []
                for col_data in col_datas:
                    col_name = col_data[1]
                    col_type = col_data[2]
                    col_name_list.append(col_name)
                    columns.append([tbl_name, col_name, col_type])
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
                        num += 1
                schema.extend(columns)

        # schema = [[0 tbl_name,1 col_name,2 col_type,3 comment,4 similarity],...]
        return schema, col_name_list, comment_list

    async def get_related_column(
        self,
        question: str,
        schema: list,
        col_name_list: list,
        comment_list: list,
    ) -> tuple[set,set]:
        column_set = set()
        strong_rala_set = set()

        length = len(col_name_list)
        embeddings = await get_embedding_list([question] + col_name_list + comment_list)
        question_embedding = embeddings[0]
        col_name_embeddings = embeddings[1:length+1]
        comment_embeddings = embeddings[length+1:]

        for idx in range(length):
            col_name_embedding = col_name_embeddings[idx]
            comment_embedding = comment_embeddings[idx]
            column = schema[idx]
            name_cos_similarity = get_cos_similarity(question_embedding, col_name_embedding)
            comment_cos_similarity = get_cos_similarity(question_embedding, comment_embedding)
            column[4] = (name_cos_similarity,comment_cos_similarity)
            # print(column[1], (name_cos_similarity,comment_cos_similarity))

        filtered_schema = [
            column for column in schema
            if column[4][0] > self.E_COL_THRESHOLD or column[4][1] > self.E_COL_THRESHOLD
        ]
        
        sort_schema = sorted(
            filtered_schema,
            key=lambda x: max(x[4][0], x[4][1]),
            reverse=True
        )[:10]

        # print(sort_schema)

        for column in sort_schema:
            name_cos_similarity = column[4][0]
            comment_cos_similarity = column[4][1]
            col_name = column[1]   
            comment = column[3]    
            if name_cos_similarity > self.E_COL_THRESHOLD:
                column_set.add(col_name)
                if name_cos_similarity > self.E_COL_STRONG_THRESHOLD:
                    # print(col_name, name_cos_similarity)
                    strong_rala_set.add(col_name)

            if comment_cos_similarity > self.E_COL_THRESHOLD:
                column_set.add(comment)
                if comment_cos_similarity > self.E_COL_STRONG_THRESHOLD:
                    # print(comment, comment_cos_similarity)
                    strong_rala_set.add(comment)

        # print(strong_rala_set)
        return column_set, strong_rala_set

    async def get_related_value(
        self, 
        question: str,
        schema: list,
    ) -> tuple[set,set]:
        value_set = set()
        strong_rala_set = set()
        async with aiosqlite.connect(self.target_db_url) as db:
            cursor = await db.cursor()
            for column in schema:
                tbl_name = column[0]
                col_name = column[1]
                col_type = column[2]
                if col_type.lower() == 'text':
                    await cursor.execute(f"SELECT {col_name} FROM {tbl_name}")
                    value_datas = await cursor.fetchall()
                    value_list = [value_data[0] for value_data in value_datas]

                    embeddings = await get_embedding_list([question] + value_list)
                    question_embedding = embeddings[0]
                    value_embeddings = embeddings[1:]
                    for enum, value in enumerate(value_list, start=0):
                        cos_similarity = get_cos_similarity(vec1=question_embedding, vec2=value_embeddings[enum])
                        if cos_similarity > self.E_VAL_THRESHOLD:
                            value_set.add(value)
                            if cos_similarity > self.E_VAL_STRONG_THRESHOLD:
                                strong_rala_set.add(value)

        return value_set, strong_rala_set

    def get_hint_str(
        self,
        entity_set
    ) -> str:
        hint_str = ""
        if len(entity_set) == 0:
            return hint_str
        hint_str = '{' + ', '.join(f'"{item}"' for item in entity_set) + '}'
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
    async def get_extractor_ans(
        self,
        prompt: str,
        llm: LLM_Base
    ) -> str:
        llm_message = [user_message(prompt)]
        response = await llm.call(messages=llm_message)
        answer = get_response_content(response=response, platform=self.platform)
        print("="*10,"ANSWER","="*10)
        print(answer)
        return answer

    async def chat(
        self,
        message: dict,
        llm: LLM_Base = None,
        vectordb: VectorDB = None,
    ):
        if message["message_to"] != EXTRACTOR:
            raise Exception("The message should not be processed by " + EXTRACTOR + 
                            ". It is sent to " + message["message_to"])
        else:
            # print("The message is being processed by " + EXTRACTOR + "...")
            schema, col_name_list, comment_list = await self.get_schema()
            hint_set = await self.get_rela_hint_keys(
                question=message['question'], vectordb=vectordb
            )
            print(hint_set)
            col_set, strong_rela_col_set = await self.get_related_column(
                question=message['question'], col_name_list=col_name_list, comment_list=comment_list, schema=schema
            )
            value_set, strong_rela_value_set = await self.get_related_value(
                question=message['question'], schema=schema
            )
            entity_set = hint_set | col_set | value_set
            strong_rela_set = strong_rela_col_set | strong_rela_value_set
            print(strong_rela_set)
            hint_str = self.get_hint_str(entity_set=entity_set)
            prompt = self.create_extractor_prompt(question=message["question"], hint_str=hint_str)
            ans = await self.get_extractor_ans(prompt=prompt, llm=llm)
            ans_list = parse_list(text=ans)
            ans_list.extend(strong_rela_set)
            distinct_ans_list = list(dict.fromkeys(ans_list))
            message["entity"] = distinct_ans_list
            message["message_to"] = FILTER
            return message
