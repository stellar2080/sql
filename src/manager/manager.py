from pyparsing import Word, alphas, oneOf, Optional, Group, ZeroOrMore, Combine, OneOrMore, White, nums

from src.utils.db_utils import connect_to_sqlite
from src.llm.api import Api
from src.agent.extractor import Extractor
from src.agent.filter import Filter
from src.agent.generator import Generator
from src.agent.reviser import Reviser
from src.llm.qwen import Qwen
from src.vectordb.vectordb import VectorDB
from src.utils.utils import deterministic_uuid, parse_list
from src.utils.const import MANAGER, REVISER, MAX_ITERATIONS, FILTER, GENERATOR, EXTRACTOR

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
            config = {}
        self.platform = config.get('platform',None)
        if self.platform is None:
            raise Exception('Plz provide platform.')
        elif self.platform == 'Api':
            self.llm = Api(config)
        elif self.platform == 'Qwen':
            self.llm = Qwen(config)

        self.url = config.get("db_path", '.')
        self.check_same_thread = config.get("check_same_thread", False)
        self.db_conn, self.dialect = connect_to_sqlite(self.url, self.check_same_thread)
        
        self.extractor = Extractor(config)
        self.filter = Filter(config)
        self.generator = Generator(config)
        self.reviser = Reviser(config)
        self.vectordb = VectorDB(config)

        self.message = None

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

    def add_doc_to_vectordb(
        self, 
        doc: str, 
        user_id: str,
        file_name: str
    ):
        print("="*30)
        result = self.parse_expression(doc)
        if result == -1:
            self.vectordb.add_tip(user_id=user_id, file_name=file_name, tip=doc)
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
                user_id=user_id, file_name=file_name, query_texts=entity, extracts=['documents','distances','metadatas']
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
                    self.vectordb.add_key(user_id=user_id, file_name=file_name, key=key, doc_id=doc_id)
                    print("="*10)
        doc = str(expression)
        key_id = deterministic_uuid(user_id+file_name+key+doc) + "-key"
        doc_id = deterministic_uuid(user_id+file_name+doc) + "-doc"
        self.vectordb.add_key(user_id=user_id, file_name=file_name, key=key, doc_id=doc_id, embedding_id=key_id)
        self.vectordb.add_doc(user_id=user_id, file_name=file_name, document=doc)

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

        for i in range(1, MAX_ITERATIONS+1):
            # print("ITERATION {}".format(i))
            # print("MESSAGE: " + str(self.message))
            if i == 0 and self.message["message_to"] is None:
                self.message["message_to"] = EXTRACTOR

            if self.message["message_to"] == MANAGER:
                # print("The message is begin processed by manager...")
                break
            elif self.message["message_to"] == EXTRACTOR:
                self.message = self.extractor.chat(message=self.message, llm=self.llm, vectordb=self.vectordb, db_conn=self.db_conn)
            elif self.message["message_to"] == FILTER:
                self.message = self.filter.chat(message=self.message, llm=self.llm, vectordb=self.vectordb, db_conn=self.db_conn)
            elif self.message["message_to"] == GENERATOR:
                self.message = self.generator.chat(message=self.message, llm=self.llm, vectordb=self.vectordb)
            elif self.message["message_to"] == REVISER:
                self.message = self.reviser.chat(message=self.message, llm=self.llm, db_conn=self.db_conn)
        return self.message