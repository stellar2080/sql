from src.agent.filter import Filter
from src.agent.decomposer import Decomposer
from src.agent.receiver import Receiver
from src.agent.reviser import Reviser
from src.exceptions import ArgsException
from src.llm.qwen import Qwen
from src.utils.utils import info, deterministic_uuid, user_message, assistant_message, error
from src.vectordb.vectordb import VectorDB
from src.utils.const import MANAGER, REVISER, MAX_ITERATIONS, FILTER, DECOMPOSER, RECEIVER


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
            self.receiver = Receiver()
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

    def train(
        self,
        schema: str = None,
        doc: list = None,
        schema_list: list = None,
        doc_list: list = None,
    ):
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
        self.vectordb.add_key(embedding_id=embedding_id,key=doc[0])
        self.vectordb.add_doc(embedding_id=embedding_id,document=doc[1])

    def clear_rag(
        self
    ):
        try:
            info("Clearing rag data...")
            self.vectordb.clear_rag()
        except Exception as e:
            error(e)

    def add_memory(self,messages:list):
        try:
            info("Adding memory...")
            memory_str = ','.join(map(str, messages))
            self.vectordb.add_memory(memory_str)
        except Exception as e:
            error(e)

    def clear_memory(self):
        try:
            info("Clearing memory data...")
            self.vectordb.clear_memory()
        except Exception as e:
            error(e)


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
            raise ArgsException("Please provide a question or a message")

        for i in range(MAX_ITERATIONS):
            info("ITERATION {}".format(i))
            info("MESSAGE: " + str(self.message))
            if i == 0 and self.message["message_to"] is None:
                self.message["message_to"] = RECEIVER

            if self.message["message_to"] == MANAGER:
                info("The message is begin processed by manager...")
                break
            elif self.message["message_to"] == RECEIVER:
                self.message = self.receiver.chat(self.message, self.llm, self.vectordb)
            elif self.message["message_to"] == FILTER:
                self.message = self.filter.chat(self.message, self.llm, self.vectordb)
            elif self.message["message_to"] == DECOMPOSER:
                self.message = self.decomposer.chat(self.message, self.llm)
            elif self.message["message_to"] == REVISER:
                self.message = self.reviser.chat(self.message, self.llm, mode="pd")

        if self.message["result"] is not None:
            mem_messages = [user_message(self.message["question"]), assistant_message(self.message["result"])]
            self.add_memory(mem_messages)
        return self.message