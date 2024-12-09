import json

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from .vectordb_base import VectorDB_Base

from src.utils.utils import deterministic_uuid, extract_documents, extract_embedding_ids
from ..utils.const import N_RESULTS_DOC


class VectorDB(VectorDB_Base):
    def __init__(self, config):
        super().__init__(config)

        path = config.get("vectordb_path", ".")
        curr_client = config.get("client", "persistent")
        host = config.get("host", None)
        port = config.get("port", None)

        default_ef = embedding_functions.DefaultEmbeddingFunction()
        self.embedding_function = config.get("embedding_function", default_ef)
        self.n_results_sql = config.get("n_results_sql", config.get("n_results", 10))
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
        self.sql_collection = self.chroma_client.get_or_create_collection(
            name="sql",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "ip"},
        )

    def generate_embedding(self, data:str, **kwargs):
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        question_sql_json = json.dumps(
            {
                "question": question,
                "sql": sql,
            },
            ensure_ascii=False,
        )
        embedding_id = deterministic_uuid(question_sql_json) + "-sql"
        self.sql_collection.add(
            documents=question_sql_json,
            embeddings=self.generate_embedding(question_sql_json),
            ids=embedding_id,
        )
        return embedding_id

    def add_schema(self, embedding_id: str, schema: str, **kwargs) -> str:
        self.schema_collection.add(
            documents=schema,
            embeddings=self.generate_embedding(schema),
            ids=embedding_id,
        )
        return embedding_id

    def add_doc(self, embedding_id: str, document: str, **kwargs) -> str:
        self.document_collection.add(
            documents=document,
            embeddings=self.generate_embedding(document),
            ids=embedding_id,
        )
        return embedding_id

    def remove_training_data(self, embedding_id: str, **kwargs) -> bool:
        if embedding_id.endswith("-sql"):
            self.sql_collection.delete(ids=[embedding_id])
            return True
        elif embedding_id.endswith("-sc"):
            self.schema_collection.delete(ids=[embedding_id])
            return True
        elif embedding_id.endswith("-doc"):
            self.document_collection.delete(ids=[embedding_id])
            return True
        else:
            return False

    def get_related_sql(self, question: str, **kwargs) -> list:
        return extract_documents(
            self.sql_collection.query(
                query_texts=[question],
                n_results=self.n_results_sql,
            )
        )

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

    def get_related_doc_ids(self, question: str, **kwargs) -> list:
        return extract_embedding_ids(
            self.document_collection.query(
                query_texts=[question],
                n_results=self.n_results_doc,
            )
        )

    def clear(self):
        try:
            self.chroma_client.delete_collection(name="document")
            self.chroma_client.delete_collection(name="schema")
            self.chroma_client.delete_collection(name="sql")

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
                name="sql",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "ip"},
            )

        except Exception as error:
            print(error)