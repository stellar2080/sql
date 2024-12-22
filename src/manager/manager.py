from src.agent.filter import Filter
from src.agent.decomposer import Decomposer
from src.agent.receiver import Receiver
from src.agent.reviser import Reviser
from src.llm.qwen import Qwen
from src.vectordb.vectordb import VectorDB
from src.utils.utils import info, deterministic_uuid, error, get_memory_str
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
                "response": None,
                "sql_result": None
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
        key_id = deterministic_uuid(key_n_doc) + "-key"
        doc_id = deterministic_uuid(doc[1]) + "-doc"
        self.vectordb.add_key(embedding_id=key_id,key=doc[0],doc_id=doc_id)
        self.vectordb.add_doc(embedding_id=doc_id,document=doc[1])

    def clear_rag(
        self
    ):
        try:
            info("Clearing rag data...")
            self.vectordb.clear_rag()
        except Exception as e:
            error(e)

    def record_memory(self):
        try:

            if self.message["sql_result"] is not None:
                memory_str = get_memory_str(["user", "assistant"],[self.message['question'],self.message["sql"]])
            elif self.message["response"] is not None:
                memory_str = get_memory_str(["user", "assistant"],[self.message['question'],self.message["response"]])
            else:
                error("Failed to record memory.")
                return
            info("Recording memory...")
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
            raise Exception("Please provide a question or a message")

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
        self.record_memory()
        return self.message