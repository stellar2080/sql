from pyparsing import Word, alphas, oneOf, Optional, Group, ZeroOrMore, Combine, OneOrMore, White, nums

from client.utils.db_utils import connect_to_sqlite
from client.llm.custom import Custom
from client.llm.tongyi import Tongyi
from client.agent.extractor import Extractor
from client.agent.filter import Filter
from client.agent.generator import Generator
from client.agent.reviser import Reviser
from client.vectordb.vectordb import VectorDB
from client.utils.utils import deterministic_uuid, parse_list
from client.utils.const import MANAGER, EXTRACTOR, FILTER, GENERATOR, REVISER

special_chars = "'_,."
word = Word(alphas + nums + special_chars)
identifier = Combine(word + ZeroOrMore(White(" ") + word))
eq_1 = Word("=")
operator_1 = oneOf("+ - * /")
lparen_1 = Word("(")
rparen_1 = Word(")")
expr = Group(
    identifier + eq_1 + OneOrMore(
        Optional(lparen_1) + identifier + Optional(operator_1 | rparen_1)
    )
)

class Manager:
    def __init__(self,config=None):
        if config is None:
            raise Exception('Please provide config.')
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
        self.vectordb = VectorDB(config)

        self.target_db_path = config.get("target_db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.db_conn, self.dialect = connect_to_sqlite(
            self.target_db_path, 
            self.check_same_thread
        )
        
        self.message = None

        self.user_id = config.get('user_id',None)

        self.MAX_ITERATIONS = config.get('MAX_ITERATIONS')

    def set_config(self, config: dict):
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
        self.vectordb = VectorDB(config)

        self.target_db_path = config.get("target_db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.db_conn, self.dialect = connect_to_sqlite(
            self.target_db_path, 
            self.check_same_thread
        )
        
        self.user_id = config.get('user_id',None)
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

    def parse_expression(
        self,
        s: str
    ):
        try:
            result_list = expr.parseString(s)[0]
            return result_list
        except Exception as e:
            return -1

    def add_to_vectordb(
        self, 
        doc: str, 
        file_name: str
    ):
        print("="*30)
        result = self.parse_expression(doc)
        if result == -1:
            self.vectordb.add_tip(
                user_id=self.user_id, file_name=file_name, tip=doc
            )
            return
        else:
            expression = [item.lower().replace('_',' ').replace('-',' ') 
                          if len(item) > 1 else item for item in result]
        key = expression[0]
        right_hand_size = expression[2:]
        for enum, entity in enumerate(right_hand_size,start=2):
            if len(entity) <= 1:
                continue
            related_keys = self.vectordb.get_related_key(
                user_id=self.user_id, 
                file_name=file_name, 
                query_texts=entity, 
                extracts=['documents','distances','metadatas']
            )
            print(related_keys)
            if len(related_keys['documents']) != 0:
                threshold = 0.1
                filtered_keys = [
                    (filtered_key, doc_id) for filtered_key, distance, doc_id in sorted(
                        zip(related_keys['documents'], related_keys['distances'], related_keys['metadatas']),
                        key=lambda x: x[1]
                    ) if distance < threshold
                ]
                print("Elem:", entity)
                print("Rela:", filtered_keys)
                if len(filtered_keys) > 0:
                    key_name = filtered_keys[0][0]
                    doc_id = filtered_keys[0][1]['doc_id']
                    if key_name != entity:
                        expression[enum] = key_name
                    self.vectordb.add_key(user_id=self.user_id, file_name=file_name, key=key, doc_id=doc_id)
                    print("="*10)
        doc = str(expression)
        key_id = deterministic_uuid(self.user_id+file_name+key+doc) + "-key"
        doc_id = deterministic_uuid(self.user_id+file_name+doc) + "-doc"
        self.vectordb.add_key(
            user_id=self.user_id, file_name=file_name, key=key, doc_id=doc_id, embedding_id=key_id
        )
        self.vectordb.add_doc(
            user_id=self.user_id, file_name=file_name, document=doc
        )

    def del_from_vectordb(
        self,
        embedding_ids
    ):
        if isinstance(embedding_ids,str):
            example = embedding_ids
        elif isinstance(embedding_ids,list):
            example = embedding_ids[0]
        if example.endswith("-key"):
            self.vectordb.delete_key(embedding_ids=embedding_ids)
        elif example.endswith("-doc"):
            self.vectordb.delete_doc(embedding_ids=embedding_ids)
        elif example.endswith("-tip"):
            self.vectordb.delete_tip(embedding_ids=embedding_ids)
            
    def get_repository(
        self,
        user_id: str,
        file_name: str
    ):
        all_keys = self.vectordb.get_all_key(
            user_id=user_id,file_name=file_name,extracts=['ids','documents','metadatas']
        )
        if len(all_keys['ids']) != 0:
            key_ids = all_keys['ids']
            keys = all_keys['documents']
            metadatas = all_keys['metadatas']
            doc_ids = []
            file_names = []
            for metadata in metadatas:
                doc_ids.append(metadata['doc_id'])
                file_names.append(metadata['file_name'])
            docs = self.vectordb.get_doc_by_id(user_id=user_id,embedding_ids=doc_ids)
            docs = [" ".join(parse_list(doc)) for doc in docs] 
            key_zip = zip(file_names, key_ids, keys, doc_ids, docs)
        else:
            key_zip = None

        all_tips = self.vectordb.get_all_tip(
            user_id=user_id,file_name=file_name,extracts=['ids','documents','metadatas']
        )
        if len(all_tips['ids']) != 0:
            tip_ids = all_tips['ids']
            tips = all_tips['documents']
            metadatas = all_keys['metadatas']
            file_names = [metadata['file_name'] for metadata in metadatas]
            tip_zip = zip(file_names, tip_ids, tips)
        else:
            tip_zip = None

        return key_zip, tip_zip
    
    def chat(
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

        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            # print("MESSAGE: " + str(self.message))
            if self.message["message_to"] == MANAGER:
                # print("The message is begin processed by manager...")
                break
            elif self.message["message_to"] == EXTRACTOR:
                self.message = self.extractor.chat(
                    message=self.message, 
                    llm=self.llm, 
                    vectordb=self.vectordb, 
                    db_conn=self.db_conn
                )
            elif self.message["message_to"] == FILTER:
                self.message = self.filter.chat(
                    message=self.message, 
                    llm=self.llm, 
                    vectordb=self.vectordb, 
                    db_conn=self.db_conn
                )
            elif self.message["message_to"] == GENERATOR:
                self.message = self.generator.chat(
                    message=self.message, 
                    llm=self.llm, 
                    vectordb=self.vectordb
                )
            elif self.message["message_to"] == REVISER:
                self.message = self.reviser.chat(
                    message=self.message, 
                    llm=self.llm, 
                    db_conn=self.db_conn
                )
                iteration += 1

        return self.message