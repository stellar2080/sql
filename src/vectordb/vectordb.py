import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from .vectordb_base import VectorDB_Base

from src.utils.utils import deterministic_uuid
from ..utils.const import N_RESULTS_KEY

class VectorDB(VectorDB_Base):
    def __init__(
        self, 
        config
    ):
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
            metadata={"hnsw:space": "cosine"},
        )
        self.key_collection = self.chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        self.tip_collection = self.chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def generate_embedding(
        self, 
        data:str, 
    ):
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    def add_doc(
        self, 
        user_id: str,
        file_name: str,
        document: str, 
        embedding_id: str = None, 
    ):
        if embedding_id is None:
            embedding_id = deterministic_uuid(user_id+file_name+document) + "-doc"
        else:
            embedding_id = embedding_id
        self.document_collection.add(
            ids=embedding_id,
            documents=document,
            embeddings=self.generate_embedding(document),
            metadatas={"user_id": user_id, "file_name": file_name}
        )
        print("Add_doc: ", document, " ID: ", embedding_id, " user_id: ", user_id, "file_name: ", file_name)

    def add_key(
        self, 
        user_id: str,
        file_name: str,
        key: str, 
        doc_id: str, 
        embedding_id: str = None, 
    ):
        if embedding_id is None:
            doc = self.document_collection.get(ids=[doc_id])['documents'][0]
            embedding_id = deterministic_uuid(user_id+file_name+key+doc) + "-key"
        self.key_collection.add(
            ids=embedding_id,
            documents=key,
            embeddings=self.generate_embedding(key),
            metadatas={"doc_id": doc_id, "user_id": user_id, "file_name": file_name}
        )
        print("Add_key: ", key, " Doc_id: ", doc_id, " user_id: ", user_id, "file_name: ", file_name)

    def add_tip(
        self, 
        user_id: str,
        file_name: str,
        tip: str, 
        embedding_id: str = None, 
    ):
        if embedding_id is None:
            embedding_id = deterministic_uuid(user_id+file_name+tip) + "-tip"
        else:
            embedding_id = embedding_id
        self.tip_collection.add(
            ids=embedding_id,
            documents=tip,
            embeddings=self.generate_embedding(tip),
            metadatas={"user_id": user_id, "file_name": file_name}
        )
        print("Add_tip: ", tip, " ID: ", embedding_id, " user_id: ", user_id, "file_name: ", file_name)

    def remove_data(
        self, 
        user_id: str,
        embedding_id: str, 
    ) -> bool:
        if embedding_id.endswith("-key"):
            self.key_collection.delete(
                ids=[embedding_id],where={"user_id":user_id})
            return True
        elif embedding_id.endswith("-doc"):
            self.document_collection.delete(
                ids=[embedding_id],where={"user_id":user_id})
            return True
        elif embedding_id.endswith("-tip"):
            self.tip_collection.delete(
                ids=[embedding_id],where={"user_id":user_id})
            return True
        else:
            return False

    def extract_query_results(
        self,
        query_results, 
        extracts
    ) -> dict:
        if query_results is None:
            return {}
        extracted_results = {}
        if isinstance(extracts, str):
            extracts = [extracts]
        for item in extracts:
            if item not in query_results:
                raise TypeError("Extract type {} is not supported.".format(item))
            extract_item = query_results[item]
            if len(extract_item) == 1:
                if isinstance(extract_item[0], list):
                    extracted_results[item] = (extract_item[0])
                elif isinstance(extract_item[0], str):
                    extracted_results[item] = ([extract_item[0]])
            else:
                extracted_results[item] = extract_item

        return extracted_results

    def get_related_doc(
        self, 
        user_id,
        file_name: str,
        query_texts, 
        n_results, 
        extracts=None, 
    ) -> dict:
        if extracts is None:
            extracts = 'documents'
        n_results = N_RESULTS_KEY if not n_results else n_results
        return self.extract_query_results(
            self.document_collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where={"$and":[{"user_id":user_id},{"file_name":file_name}]}
            ),
            extracts=extracts
        )

    def get_related_key(
        self, 
        user_id,
        file_name: str,
        query_texts, 
        n_results=None, 
        extracts=None, 
    ) -> dict:
        if extracts is None:
            extracts = 'documents'
        n_results = N_RESULTS_KEY if not n_results else n_results
        return self.extract_query_results(
            self.key_collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where={"$and":[{"user_id":user_id},{"file_name":file_name}]}
            ),
            extracts=extracts
        )
    
    def get_related_tip(
        self, 
        user_id,
        file_name: str,
        query_texts, 
        n_results=None, 
        extracts=None, 
    ) -> dict:
        if extracts is None:
            extracts = 'documents'
        n_results = N_RESULTS_KEY if not n_results else n_results
        return self.extract_query_results(
            self.tip_collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where={"$and":[{"user_id":user_id},{"file_name":file_name}]}
            ),
            extracts=extracts
        )

    def get_doc_by_id(
        self,
        user_id,
        embedding_ids,
    ):
        if isinstance(embedding_ids,str):
            result = self.document_collection.get(
                ids=[embedding_ids],where={"user_id":user_id})
            return result['documents'][0]
        elif isinstance(embedding_ids,list):
            ids_set = set(embedding_ids)
            if len(ids_set) == len(embedding_ids):
                result = self.document_collection.get(
                    ids=embedding_ids,where={"user_id":user_id})
                return result['documents']
            else:
                distinct_ids = list(dict.fromkeys(embedding_ids))
                result = self.document_collection.get(
                    ids=distinct_ids,where={"user_id":user_id})
                docs = result['documents']
                ids_dict = {}
                for id,doc in zip(distinct_ids,docs):
                    ids_dict[id] = doc
                ret_list = [ids_dict[id] for id in embedding_ids]
                return ret_list

    def get_all_key(
        self,
        user_id,
        file_name,
        extracts = None
    ):
        if extracts is None:
            extracts = 'documents'
        res = self.extract_query_results(
            self.key_collection.get(
                where={"$and":[{"user_id":user_id},{"file_name":file_name}]}
            ),
            extracts=extracts
        )
        return res

    def get_all_doc(
        self,
        user_id,
        file_name,
        extracts = None
    ):
        if extracts is None:
            extracts = 'documents'
        res = self.extract_query_results(
            self.document_collection.get(
                where={"$and":[{"user_id":user_id},{"file_name":file_name}]}
            ),
            extracts=extracts
        )
        return res
    
    def get_all_tip(
        self,
        user_id,
        file_name,
        extracts = None
    ):
        if extracts is None:
            extracts = 'documents'
        res = self.extract_query_results(
            self.tip_collection.get(
                where={"$and":[{"user_id":user_id},{"file_name":file_name}]}
            ),
            extracts=extracts
        )
        return res