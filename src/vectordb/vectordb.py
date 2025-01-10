import json
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from .vectordb_base import VectorDB_Base
import time

from src.utils.utils import deterministic_uuid
from ..utils.const import N_RESULTS_DOC, N_RESULTS_KEY, N_RESULTS_SC

class VectorDB(VectorDB_Base):
    def __init__(self, config):
        super().__init__(config)

        path = config.get("vectordb_path", None)
        curr_client = config.get("vectordb_client", "persistent")
        host = config.get("vectordb_host", None)
        port = config.get("vectordb_port", None)

        default_ef = embedding_functions.DefaultEmbeddingFunction()
        self.embedding_function = config.get("embedding_function", default_ef)

        self.chroma_client = None

        if curr_client == "persistent":
            self.chroma_client = chromadb.PersistentClient(
                path=path, settings=Settings(anonymized_telemetry=False)
            )
        elif curr_client == "http":
            self.chroma_client = chromadb.HttpClient(host=host, port=port)
        elif curr_client == "ephemeral":
            self.chroma_client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
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

    def generate_embedding(self, data:str, **kwargs):
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    def add_schema(self, schema: str, embedding_id: str = None,**kwargs):
        if embedding_id is None:
            embedding_id = deterministic_uuid(schema) + "-sc"
        else:
            embedding_id = embedding_id
        self.schema_collection.add(
            ids=embedding_id,
            documents=schema,
            embeddings=self.generate_embedding(schema),
        )

    def add_doc(self, document: str, embedding_id: str = None, **kwargs):
        if embedding_id is None:
            embedding_id = deterministic_uuid(document) + "-doc"
        else:
            embedding_id = embedding_id
        self.document_collection.add(
            ids=embedding_id,
            documents=document,
            embeddings=self.generate_embedding(document),
        )

    def add_key(self, key: str, doc_id: str, embedding_id: str = None, **kwargs):
        self.key_collection.add(
            ids=embedding_id,
            documents=key,
            embeddings=self.generate_embedding(key),
            metadatas={"doc_id": doc_id}
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
        else:
            return False

    def extract_query_results(self,query_results, extracts) -> list:
        if query_results is None:
            return []
        extracted_results = []
        if isinstance(extracts, str):
            extracts = [extracts]
        for item in extracts:
            if item not in query_results:
                raise TypeError("Extract type {} is not supported.".format(item))
            extract_item = query_results[item]
            if len(extract_item) == 1:
                if isinstance(extract_item[0], list):
                    extracted_results.append(extract_item[0])
                elif isinstance(extract_item[0], str):
                    extracted_results.append([extract_item[0]])

        if len(extracted_results) == 1:
            return extracted_results[0]
        return extracted_results

    def get_related_schema(self, question: str, **kwargs) -> list:
        return self.extract_query_results(
            self.schema_collection.query(
                query_texts=[question],
                n_results=N_RESULTS_SC,
            ),
            extracts='documents'
        )

    def get_related_doc(self, question: str, **kwargs) -> list:
        return self.extract_query_results(
            self.document_collection.query(
                query_texts=[question],
                n_results=N_RESULTS_DOC,
            ),
            extracts='documents'
        )

    def get_related_key(self, question: str, **kwargs) -> list:
        return self.extract_query_results(
            self.key_collection.query(
                query_texts=[question],
                n_results=N_RESULTS_KEY,
            ),
            extracts='documents'
        )

    def get_related_key_ids(self, question: str, **kwargs) -> list:
        return self.extract_query_results(
            self.key_collection.query(
                query_texts=[question],
                n_results=N_RESULTS_KEY,
            ),
            extracts='ids'
        )

    def get_related_key_meta(self, question: str, **kwargs) -> list:
        res = self.extract_query_results(
            self.key_collection.query(
                query_texts=[question],
                n_results=N_RESULTS_KEY,
            ),
            extracts='metadatas'
        )
        return [item['doc_id'] for item in res]

    def get_doc_by_id(
        self,
        embedding_ids,
    ):
        if isinstance(embedding_ids,str):
            result = self.document_collection.get(ids=[embedding_ids])
            return result['documents'][0]
        elif isinstance(embedding_ids,list):
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
            print(error)