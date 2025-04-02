from client.llm.custom import Custom
from client.llm.tongyi import Tongyi
from client.agent.extractor import Extractor
from client.agent.filter import Filter
from client.agent.generator import Generator
from client.agent.reviser import Reviser
from client.vectordb.vectordb import VectorDB
from client.utils.utils import deterministic_uuid, parse_list
from client.utils.const import MANAGER, EXTRACTOR, FILTER, GENERATOR, REVISER

class Manager:
    def __init__(self,config=None):
        if config is None:
            raise Exception('Please provide config.')
        vectordb_only = config.get('vectordb_only')
        if vectordb_only:
            self.vectordb = VectorDB(config)
            self.user_id = config.get('user_id',None)
        else:
            self.platform = config.get('platform',None)
            if self.platform is None:
                raise Exception('Please provide platform.')
            elif self.platform == 'Custom':
                self.llm = Custom(config)
            elif self.platform == 'Tongyi':
                self.llm = Tongyi(config)

            self.extractor = Extractor(config)
            self.filter = Filter(config)
            self.generator = Generator(config)
            self.reviser = Reviser(config)
            self.user_id = config.get('user_id',None)
            self.vectordb = VectorDB(config)

            self.dialect = "sqlite"
            
            self.message = None

            self.MAX_ITERATIONS = config.get('MAX_ITERATIONS')

    def message_init(self):
        self.message = {
            "question": None,
            "entity": None,
            "dialect": self.dialect,
            "schema": None,
            "hint": None,
            "sql": None,
            "sql_result": None,
            "message_to": EXTRACTOR
        }

    def add_doc(
        self, 
        doc: str, 
    ):
        self.vectordb.add_data(user_id=self.user_id,doc=doc)
            
    async def get_repository(
        self,
        user_id: str,
    ):
        all_keys = await self.vectordb.get_all_key(
            user_id=user_id,extracts=['ids','documents','metadatas']
        )
        if len(all_keys['ids']) != 0:
            key_ids = all_keys['ids']
            keys = all_keys['documents']
            metadatas = all_keys['metadatas']
            doc_ids = []
            for metadata in metadatas:
                doc_ids.append(metadata['doc_id'])
            docs = await self.vectordb.get_doc_by_id(user_id=user_id,embedding_ids=doc_ids)
            docs = [" ".join(parse_list(doc)) for doc in docs] 
            key_zip = zip(key_ids, keys, doc_ids, docs)
        else:
            key_zip = None

        all_tips = await self.vectordb.get_all_tip(
            user_id=user_id,extracts=['ids','documents','metadatas']
        )
        if len(all_tips['ids']) != 0:
            tip_ids = all_tips['ids']
            tips = all_tips['documents']
            metadatas = all_keys['metadatas']
            tip_zip = zip(tip_ids, tips)
        else:
            tip_zip = None

        return key_zip, tip_zip
    
    async def remove_doc(
        self, 
        embedding_id: str | list,
        user_id: str = None,
    ):
        await self.vectordb.remove_data(embedding_id=embedding_id,user_id=user_id)
    
    async def chat(
        self,
        question: str = None,
        message: dict = None,
    ):
        if question is not None:
            self.message_init()
            self.message["question"] = question
        elif message is not None:
            self.message = message
        else:
            raise Exception("Please provide a question or a message")
        
        if self.message["message_to"] is None:
            self.message["message_to"] = EXTRACTOR

        yield self.message
        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            # print("MESSAGE: " + str(self.message))
            if self.message["message_to"] == MANAGER:
                # print("The message is begin processed by manager...")
                break

            elif self.message["message_to"] == EXTRACTOR:
                self.message = await self.extractor.chat(
                    message=self.message, 
                    llm=self.llm, 
                    vectordb=self.vectordb, 
                )
                yield self.message
            elif self.message["message_to"] == FILTER:
                self.message = await self.filter.chat(
                    message=self.message, 
                    llm=self.llm, 
                    vectordb=self.vectordb, 
                )
                yield self.message
            elif self.message["message_to"] == GENERATOR:
                self.message = await self.generator.chat(
                    message=self.message, 
                    llm=self.llm, 
                    vectordb=self.vectordb
                )
                yield self.message
            elif self.message["message_to"] == REVISER:
                self.message = await self.reviser.chat(
                    message=self.message, 
                    llm=self.llm, 
                )
                iteration += 1

        yield self.message