import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from .vectordb_base import VectorDB_Base

from client.utils.utils import deterministic_uuid

class VectorDB(VectorDB_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__(config)

        self.chroma_client = None
        self.host = config.get("vectordb_host", None)
        self.port = config.get("vectordb_port", None)

        default_ef = embedding_functions.DefaultEmbeddingFunction()
        self.embedding_function = config.get("embedding_function", default_ef)
        self.N_RESULTS = config.get("N_RESULTS")

    async def generate_embedding(
        self, 
        data:str, 
    ):
        embedding = await self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    async def add_doc(
        self, 
        user_id: str,
        file_name: str,
        document: str, 
        embedding_id: str = None, 
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if embedding_id is None:
            embedding_id = deterministic_uuid(user_id+file_name+document) + "-doc"
        else:
            embedding_id = embedding_id

        await document_collection.add(
            ids=embedding_id,
            documents=document,
            embeddings=await self.generate_embedding(document),
            metadatas={"user_id": user_id, "file_name": file_name}
        )
        print("Add_doc: ", document, " ID: ", embedding_id, " user_id: ", user_id, "file_name: ", file_name)

    async def add_key(
        self, 
        user_id: str,
        file_name: str,
        key: str, 
        doc_id: str, 
        embedding_id: str = None, 
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

        if embedding_id is None:
            doc = await document_collection.get(ids=[doc_id])['documents'][0]
            embedding_id = deterministic_uuid(user_id+file_name+key+doc) + "-key"
        key_collection.add(
            ids=embedding_id,
            documents=key,
            embeddings=await self.generate_embedding(key),
            metadatas={"doc_id": doc_id, "user_id": user_id, "file_name": file_name}
        )
        print("Add_key: ", key, " Key_Rela_Doc_id: ", doc_id, " user_id: ", user_id, "file_name: ", file_name)

    async def add_tip(
        self, 
        user_id: str,
        file_name: str,
        tip: str, 
        embedding_id: str = None, 
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if embedding_id is None:
            embedding_id = deterministic_uuid(user_id+file_name+tip) + "-tip"
        else:
            embedding_id = embedding_id
        await tip_collection.add(
            ids=embedding_id,
            documents=tip,
            embeddings=await self.generate_embedding(tip),
            metadatas={"user_id": user_id, "file_name": file_name}
        )
        print("Add_tip: ", tip, " ID: ", embedding_id, " user_id: ", user_id, "file_name: ", file_name)

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

    async def get_related_doc(
        self, 
        query_texts, 
        user_id: str = None,
        file_name: str = None,
        n_results=None, 
        extracts=None, 
    ) -> dict:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None

        if extracts is None:
            extracts = 'documents'
        n_results = self.N_RESULTS if not n_results else n_results
        return self.extract_query_results(
            await document_collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where_dict
            ),
            extracts=extracts
        )

    async def get_related_key(
        self, 
        query_texts, 
        user_id: str = None,
        file_name: str = None,
        n_results=None, 
        extracts=None, 
    ) -> dict:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None

        if extracts is None:
            extracts = 'documents'
        n_results = self.N_RESULTS if not n_results else n_results
        return self.extract_query_results(
            await key_collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where_dict
            ),
            extracts=extracts
        )
    
    async def get_related_tip(
        self, 
        query_texts,
        user_id: str = None,
        file_name: str = None,   
        n_results=None, 
        extracts=None, 
    ) -> dict:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None

        if extracts is None:
            extracts = 'documents'
        n_results = self.N_RESULTS if not n_results else n_results
        return self.extract_query_results(
            await tip_collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where_dict
            ),
            extracts=extracts
        )

    async def get_doc_by_id(
        self,
        user_id,
        embedding_ids,
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if isinstance(embedding_ids,str):
            result = await document_collection.get(
                ids=[embedding_ids],where={"user_id":user_id}
            )
            return result['documents'][0]
        elif isinstance(embedding_ids,list):
            ids_set = set(embedding_ids)
            if len(ids_set) == len(embedding_ids):
                result = await document_collection.get(
                    ids=embedding_ids,where={"user_id":user_id}
                )
                return result['documents']
            else:
                distinct_ids = list(dict.fromkeys(embedding_ids))
                result = await document_collection.get(
                    ids=distinct_ids,where={"user_id":user_id}
                )
                docs = result['documents']
                ids_dict = {}
                for id,doc in zip(distinct_ids,docs):
                    ids_dict[id] = doc
                ret_list = [ids_dict[id] for id in embedding_ids]
                return ret_list

    async def get_all_key(
        self,
        user_id: str = None,
        file_name: str = None,
        extracts = None
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None

        if extracts is None:
            extracts = 'documents'
        res = self.extract_query_results(
            await key_collection.get(
                where=where_dict
            ),
            extracts=extracts
        )
        return res

    async def get_all_doc(
        self,
        user_id: str = None,
        file_name: str = None,
        extracts = None
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None

        if extracts is None:
            extracts = 'documents'
        res = self.extract_query_results(
            await document_collection.get(
                where=where_dict
            ),
            extracts=extracts
        )
        return res
    
    async def get_all_tip(
        self,
        user_id: str = None,
        file_name: str = None,
        extracts = None
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None

        if extracts is None:
            extracts = 'documents'
        res = self.extract_query_results(
            await tip_collection.get(
                where=where_dict
            ),
            extracts=extracts
        )
        return res
    
    async def delete_key(
        self, 
        embedding_ids
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if isinstance(embedding_ids,str):
            await key_collection.delete(
                ids=[embedding_ids]
            )
        elif isinstance(embedding_ids,list):
            await key_collection.delete(
                ids=embedding_ids
            )
    
    async def delete_doc(
        self, 
        embedding_ids
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

        if isinstance(embedding_ids,str):
            await document_collection.delete(
                ids=[embedding_ids]
            )
        elif isinstance(embedding_ids,list):
            await document_collection.delete(
                ids=embedding_ids
            )
            
    async def delete_tip(
        self, 
        embedding_ids
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if isinstance(embedding_ids,str):
            await tip_collection.delete(
                ids=[embedding_ids]
            )
        elif isinstance(embedding_ids,list):
            await tip_collection.delete(
                ids=embedding_ids
            )

    async def remove_data(
        self, 
        embedding_id: str,
        user_id: str = None,
        file_name: str = None,
    ) -> bool:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id and file_name:
            where_dict = {"$and":[{"user_id":user_id},{"file_name":file_name}]}
        elif user_id:
            where_dict = {"user_id":user_id}
        elif file_name:
            where_dict = {"file_name":file_name}
        else:
            where_dict = None
            
        if embedding_id.endswith("-key"):
            await key_collection.delete(
                ids=[embedding_id],where=where_dict
            )
            return True
        elif embedding_id.endswith("-doc"):
            await document_collection.delete(
                ids=[embedding_id],where=where_dict
            )
            return True
        elif embedding_id.endswith("-tip"):
            await tip_collection.delete(
                ids=[embedding_id],where=where_dict
            )
            return True
        else:
            return False