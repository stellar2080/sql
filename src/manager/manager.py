import os

from pyparsing import Word, alphas, oneOf, Optional, Group, ZeroOrMore, Combine, OneOrMore, White, nums, Suppress

from src.agent.extractor import Extractor
from src.agent.filter import Filter
from src.agent.decomposer import Decomposer
from src.agent.reviser import Reviser
from src.llm.qwen import Qwen
from src.vectordb.vectordb import VectorDB
from src.utils.utils import deterministic_uuid
from src.utils.const import MANAGER, REVISER, MAX_ITERATIONS, FILTER, DECOMPOSER, EXTRACTOR


class Manager:
    def __init__(self,config=None):
        if config is None:
            config = {}
        self.mode = config.get('mode',None)
        if self.mode is None or self.mode == 'run':
            print("running mode")
            self.platform = config.get('platform',None)
            if self.platform is None or self.platform == 'Qwen':
                self.llm = Qwen(config)
            self.extractor = Extractor()
            self.filter = Filter()
            self.decomposer = Decomposer()
            self.reviser = Reviser(config)
            self.message = {
                "question": None,
                "sql": None,
                "schema": None,
                "evidence": None,
                "message_to": None,
                "response": None,
                "sql_result": None
            }
        elif self.mode == 'train':
            print("training mode")
        self.vectordb = VectorDB(config)

    def train_schema(
        self,
        schema: str = None,
    ):
        self.vectordb.add_schema(schema=schema)

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

            eq_2 = Suppress("=")
            operator_2 = Suppress(oneOf("+ - * /"))
            lparen_2 = Suppress("(")
            rparen_2 = Suppress(")")

            expr_all = Group(
                identifier + eq_1 + OneOrMore(
                    Optional(lparen_1) + identifier + Optional(operator_1 | rparen_1)
                )
            )
            expr_sup = Group(
                identifier + eq_2 + OneOrMore(
                    Optional(lparen_2) + identifier + Optional(operator_2 | rparen_2)
                )
            )

            with open(path, mode="r") as f:
                content = f.readlines()
                for line in content:
                    print("="*30)
                    result_all = list(expr_all.parseString(line)[0])
                    result_sup = list(expr_sup.parseString(line)[0])
                    key = result_all[0]
                    print(result_all)
                    print(result_sup)
                    for num, item in enumerate(result_sup[1:]):
                        lower_name = item.lower()
                        results = self.vectordb.key_collection.query(query_texts=lower_name)
                        threshold = 0.1
                        filtered_keys = [
                            (f_key, doc_id) for f_key, distance, doc_id in sorted(
                                zip(results['documents'][0], results['distances'][0], results['metadatas'][0]),
                                key=lambda x: x[1]
                            ) if distance < threshold
                        ]
                        print("Elem:", item)
                        print("Rela:", filtered_keys)
                        if len(filtered_keys) > 0:
                            f_key = filtered_keys[0][0]
                            doc_id = filtered_keys[0][1]['doc_id']
                            if f_key != lower_name:
                                result_all[result_all.index(item)] = f_key
                            self.vectordb.add_key(key=key, doc_id=doc_id)
                            print("="*10)
                    doc = " ".join(result_all)
                    key_n_doc = key + ": " + doc
                    key_id = deterministic_uuid(key_n_doc) + "-key"
                    doc_id = deterministic_uuid(doc) + "-doc"
                    self.vectordb.add_key(key=key, doc_id=doc_id, embedding_id=key_id)
                    self.vectordb.add_doc(document=doc)
            print(f"Doc:{path} has been trained")
        except Exception as e:
            print(e)


    def clear_rag(
        self
    ):
        try:
            print("Clearing rag data...")
            self.vectordb.clear_rag()
        except Exception as e:
            print(e)

    def chat(
        self,
        question: str = None,
        message: dict = None,
    ):
        if question is not None:
            self.message["question"] = question
        elif message is not None:
            self.message = message
        else:
            raise Exception("Please provide a question or a message")

        for i in range(MAX_ITERATIONS):
            print("ITERATION {}".format(i))
            print("MESSAGE: " + str(self.message))
            if i == 0 and self.message["message_to"] is None:
                self.message["message_to"] = EXTRACTOR

            if self.message["message_to"] == MANAGER:
                print("The message is begin processed by manager...")
                break
            elif self.message["message_to"] == EXTRACTOR:
                self.message = self.extractor.chat(self.message, self.llm)
            elif self.message["message_to"] == FILTER:
                self.message = self.filter.chat(self.message, self.llm, self.vectordb)
            elif self.message["message_to"] == DECOMPOSER:
                self.message = self.decomposer.chat(self.message, self.llm)
            elif self.message["message_to"] == REVISER:
                self.message = self.reviser.chat(self.message, self.llm)
        return self.message