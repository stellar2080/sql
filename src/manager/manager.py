from torch.nn.functional import embedding

from src.agent.filter import Filter
from src.agent.decomposer import Decomposer
from src.agent.reviser import Reviser
from src.exceptions import AgentTypeException, ArgsException, LLMTypeException
from src.llm.qwen import Qwen
from src.utils.utils import info, deterministic_uuid
from src.vectordb.vectordb import VectorDB
from src.db.mapdb import MapDB
from src.utils.const import MANAGER, REVISER, MAX_ITERATIONS, FILTER, DECOMPOSER, AGENT_LIST


class Manager:
    def __init__(self,config=None):
        if config is None:
            config = {}
        self.mode = config.get('mode',None)
        if self.mode is None or self.mode == 'run':
            info("running mode")
            self.platform = config.get('platform',None)
            if self.platform is None or self.platform == 'Qwen':
                self.llm = Qwen(config)
            self.filter = Filter()
            self.decomposer = Decomposer()
            self.reviser = Reviser(config)
            self.message = {
                "question": None,
                "sql": None,
                "schema": None,
                "evidence": None,
                "message_to": None,
                "result": None
            }
        elif self.mode == 'train':
            info("training mode")
        self.vectordb = VectorDB(config)
        self.mapdb = MapDB(config)

    def train(
        self,
        question: str = None,
        sql: str = None,
        schema: str = None,
        doc: list = None,
        schema_list: list = None,
        doc_list: list = None,
    ):
        if question and sql:
            info("Adding sql...")
            self.vectordb.add_question_sql(question=question, sql=sql)
        if schema:
            info("Adding schema...")
            self.train_schema(schema)
        if doc:
            info("Adding document...")
            self.train_doc(doc)
        if schema_list:
            info("Adding schema in the list...")
            for schema in schema_list:
                self.train_schema(schema=schema)
            pass
        if doc_list:
            info("Adding document in the list...")
            for doc in doc_list:
                self.train_doc(doc=doc)

    def train_schema(
        self,
        schema: str = None,
    ):
        embedding_id = deterministic_uuid(schema) + "-sc"
        self.vectordb.add_schema(embedding_id=embedding_id,schema=schema)

    def train_doc(
        self,
        doc: list = None,
    ):
        key_n_doc = doc[0] + ": " +  doc[1]
        embedding_id = deterministic_uuid(key_n_doc) + "-doc"
        self.vectordb.add_doc(embedding_id=embedding_id,document=doc[0])
        self.mapdb.add_doc(embedding_id=embedding_id,document=doc[1])

    def clear(
        self
    ):
        self.vectordb.clear()
        self.mapdb.clear()

    def chat(
        self,
        question=None,
        sql=None,
        schema=None,
        message_to=None
    ):
        if question is not None:
            self.message["question"] = question
        else:
            raise ArgsException("Please provide a question")
        if sql is not None:
            self.message["sql"] = sql
        if schema is not None:
            self.message["schema"] = schema

        if message_to is None:
            self.message["message_to"] = MANAGER
        elif self.message["message_to"] not in AGENT_LIST:
            raise AgentTypeException("Agent Type Error")
        else:
            self.message["message_to"] = message_to

        for i in range(MAX_ITERATIONS):
            info("ITERATION {}".format(i))
            info("MESSAGE: " + str(self.message))
            if i == 0:
                self.message["message_to"] = FILTER

            if self.message["message_to"] == MANAGER:
                info("The message is begin processed by manager...")
                break
            elif self.message["message_to"] == FILTER:
                self.message = self.filter.chat(self.message, self.llm, self.vectordb, self.mapdb)
            elif self.message["message_to"] == DECOMPOSER:
                self.message = self.decomposer.chat(self.message, self.llm)
            elif self.message["message_to"] == REVISER:
                self.message = self.reviser.chat(self.message, self.llm)
        # for key, value in self.message.items():
        #     print(f"{key}: {value}")
        return self.message