import os
import sqlite3
from urllib.parse import urlparse
from pyparsing import Word, alphas, oneOf, Optional, Group, ZeroOrMore, Combine, OneOrMore, White, nums, Suppress
import requests

from src.llm.api import Api
from src.agent.extractor import Extractor
from src.agent.filter import Filter
from agent.generator import Generator
from src.agent.reviser import Reviser
from src.llm.qwen import Qwen
from src.vectordb.vectordb import VectorDB
from src.utils.utils import deterministic_uuid
from src.utils.const import MANAGER, REVISER, MAX_ITERATIONS, FILTER, GENERATOR, EXTRACTOR


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
        self.db_conn, self.dialect = self.connect_to_sqlite(self.url, self.check_same_thread)
        
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

    def connect_to_sqlite(
        self,
        url: str,
        check_same_thread: bool = False,
        **kwargs
    ):
        if not os.path.exists(url):
            path = os.path.basename(urlparse(url).path)
            response = requests.get(url)
            response.raise_for_status()
            with open(path, "wb") as f:
                f.write(response.content)
        conn = sqlite3.connect(
            url,
            check_same_thread=check_same_thread,
            **kwargs
        )
        dialect = "sqlite"
        return conn, dialect

    def train_doc(self, path):
        if not os.path.exists(path):
            raise Exception("Path does not exist.")
        try:
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

            with open(path, mode="r") as f:
                content = f.readlines()
                for line in content:
                    print("="*30)
                    expression = [item.lower().replace('_',' ').replace('-',' ') if len(item) > 1 else item
                                  for item in list(expr.parseString(line)[0])]
                    key = expression[0]
                    right_hand_size = expression[2:]
                    for enum, entity in enumerate(right_hand_size,start=2):
                        if len(entity) <= 1:
                            continue
                        related_keys = self.vectordb.get_related_key(query_texts=entity, extracts=['documents','distances','metadatas'])
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
                                filtered_key = filtered_keys[0][0]
                                doc_id = filtered_keys[0][1]['doc_id']
                                if filtered_key != entity:
                                    expression[enum] = filtered_key
                                self.vectordb.add_key(key=key, doc_id=doc_id)
                                print("="*10)
                    doc = str(expression)
                    key_n_doc = key + ": " + doc
                    key_id = deterministic_uuid(key_n_doc) + "-key"
                    doc_id = deterministic_uuid(doc) + "-doc"
                    self.vectordb.add_key(key=key, doc_id=doc_id, embedding_id=key_id)
                    self.vectordb.add_doc(document=doc)
            print(f"Doc:{path} has been trained")
        except Exception as e:
            print(e)

    def clear_doc(
        self
    ):
        try:
            print("Clearing rag data...")
            self.vectordb.clear_doc()
        except Exception as e:
            print(e)

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
                self.message = self.generator.chat(message=self.message, llm=self.llm)
            elif self.message["message_to"] == REVISER:
                self.message = self.reviser.chat(message=self.message, llm=self.llm, db_conn=self.db_conn)
        return self.message