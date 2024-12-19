import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from .vectordb_base import VectorDB_Base
import time

from src.utils.utils import extract_documents, extract_embedding_ids, info, deterministic_uuid
from ..utils.const import N_RESULTS_DOC, N_RESULTS_KEY


class VectorDB(VectorDB_Base):
    def __init__(self, config):
        super().__init__(config)

        path = config.get("vectordb_path", ".")
        curr_client = config.get("client", "persistent")
        host = config.get("host", None)
        port = config.get("port", None)

        default_ef = embedding_functions.DefaultEmbeddingFunction()
        self.embedding_function = config.get("embedding_function", default_ef)
        self.n_results_key = config.get("n_results_key", config.get("n_results", N_RESULTS_KEY))
        self.n_results_doc = config.get("n_results_doc", config.get("n_results", N_RESULTS_DOC))
        self.n_results_schema = config.get("n_results_schema", config.get("n_results", 10))

        self.chroma_client = None

        if curr_client == "persistent":
            self.chroma_client = chromadb.PersistentClient(
                path=path, settings=Settings(anonymized_telemetry=False)
            )
        elif curr_client == "http":
            self.chroma_client = chromadb.HttpClient(host=host, port=port)
        elif curr_client == "in-memory":
            self.chroma_client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
        elif isinstance(curr_client, chromadb.api.client.Client):
            self.chroma_client = curr_client
        else:
            raise TypeError(f"Unknown client type or it is unsupported: {curr_client}")

        self.document_collection = self.chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "ip"},
        )
        self.schema_collection = self.chroma_client.get_or_create_collection(
            name="schema",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "ip"},
        )
        self.key_collection = self.chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "ip"},
        )
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name="memory",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "ip"},
        )

    def generate_embedding(self, data:str, **kwargs):
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    def add_schema(self, embedding_id: str, schema: str, **kwargs):
        self.schema_collection.add(
            ids=embedding_id,
            documents=schema,
            embeddings=self.generate_embedding(schema),
        )

    def add_doc(self, embedding_id: str, document: str, **kwargs):
        self.document_collection.add(
            ids=embedding_id,
            documents=document,
            embeddings=self.generate_embedding(document),
        )

    def add_key(self, embedding_id: str, key: str, **kwargs):
        self.key_collection.add(
            ids=embedding_id,
            documents=key,
            embeddings=self.generate_embedding(key),
        )

    def add_memory(self, memory: str, **kwargs):
        timestamp = time.time()
        info(timestamp)
        embedding_id = deterministic_uuid(memory) + "-mem"
        self.memory_collection.add(
            ids=embedding_id,
            documents=memory,
            embeddings=self.generate_embedding(memory),
            metadatas={"Timestamp": timestamp},
        )

    def remove_data(self, embedding_id: str, **kwargs) -> bool:
        if embedding_id.endswith("-key"):
            self.key_collection.delete(ids=[embedding_id])
            return True
        elif embedding_id.endswith("-sc"):
            self.schema_collection.delete(ids=[embedding_id])
            return True
        elif embedding_id.endswith("-doc"):
            self.document_collection.delete(ids=[embedding_id])
            return True
        elif embedding_id.endswith("-mem"):
            self.memory_collection.delete(ids=[embedding_id])
            return True
        else:
            return False

    def get_related_schema(self, question: str, **kwargs) -> list:
        return extract_documents(
            self.schema_collection.query(
                query_texts=[question],
                n_results=self.n_results_schema,
            )
        )

    def get_related_doc(self, question: str, **kwargs) -> list:
        return extract_documents(
            self.document_collection.query(
                query_texts=[question],
                n_results=self.n_results_doc,
            )
        )

    def get_related_key(self, question: str, **kwargs) -> list:
        return extract_documents(
            self.key_collection.query(
                query_texts=[question],
                n_results=self.n_results_key,
            )
        )

    def get_related_key_ids(self, question: str, **kwargs) -> list:
        return extract_embedding_ids(
            self.key_collection.query(
                query_texts=[question],
                n_results=self.n_results_key,
            )
        )

    def get_doc_by_id(
        self,
        embedding_ids,
    ):
        if type(embedding_ids) == str:
            result = self.document_collection.get(ids=[embedding_ids])
            return result['documents'][0]
        elif type(embedding_ids) == list:
            result = self.document_collection.get(ids=embedding_ids)
            return result['documents']

    def clear_rag(self):
        try:
            self.chroma_client.delete_collection(name="document")
            self.chroma_client.delete_collection(name="schema")
            self.chroma_client.delete_collection(name="key")

            self.chroma_client.create_collection(
                name="document",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "ip"},
            )
            self.chroma_client.create_collection(
                name="schema",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "ip"},
            )
            self.chroma_client.create_collection(
                name="key",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "ip"},
            )

        except Exception as error:
            info(error)

    def clear_memory(self):
        try:
            self.chroma_client.delete_collection(name="memory")

            self.chroma_client.create_collection(
                name="memory",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "ip"},
            )

        except Exception as error:
            info(error)