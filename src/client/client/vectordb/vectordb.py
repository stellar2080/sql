import chromadb
from chromadb.utils import embedding_functions
from .vectordb_base import VectorDB_Base
from pyparsing import Word, alphas, oneOf, Optional, Group, ZeroOrMore, Combine, OneOrMore, White, nums
from client.utils.utils import deterministic_uuid

class VectorDB(VectorDB_Base):
    def __init__(
        self, 
        config
    ):
        super().__init__(config)

        self.host = config.get("vectordb_host", None)
        self.port = config.get("vectordb_port", None)

        default_ef = embedding_functions.DefaultEmbeddingFunction()
        self.embedding_function = config.get("embedding_function", default_ef)
        self.N_RESULTS = config.get("N_RESULTS", 3)

    def generate_embedding(
        self, 
        data:str, 
    ):
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    async def add_doc(
        self, 
        user_id: str,
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
            embedding_id = deterministic_uuid(user_id+document) + "-doc"
        else:
            embedding_id = embedding_id

        await document_collection.add(
            ids=embedding_id,
            documents=document,
            embeddings=self.generate_embedding(document),
            metadatas={"user_id": user_id, "key_num": 0}
        )
        print("Add_doc: ", document, " ID: ", embedding_id, " user_id: ", user_id, "key_num: ", 0)

    async def add_key(
        self, 
        user_id: str,
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

        res = await document_collection.get(ids=[doc_id])
        doc = res['documents'][0]

        if embedding_id is None:
            embedding_id = deterministic_uuid(user_id+key+doc) + "-key"

        results = await key_collection.get(ids=embedding_id)
        existed_docs = results['documents']
        if len(existed_docs) == 0:
            await key_collection.add(
                ids=embedding_id,
                documents=key,
                embeddings=self.generate_embedding(key),
                metadatas={"doc_id": doc_id, "user_id": user_id, "activated": 1}
            )
            print("Add_key: ", key, " Key_Rela_Doc_id: ", doc_id, " user_id: ", user_id)

            key_num = res['metadatas'][0]['key_num'] + 1
            await document_collection.update(
                ids=doc_id,
                metadatas={"user_id": user_id, "key_num": key_num}
            )
            print("Update_doc: ", doc, " ID: ", doc_id, " user_id: ", user_id, "key_num: ", key_num)

    async def add_tip(
        self, 
        user_id: str,
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
            embedding_id = deterministic_uuid(user_id+tip) + "-tip"
        else:
            embedding_id = embedding_id
        await tip_collection.add(
            ids=embedding_id,
            documents=tip,
            embeddings=self.generate_embedding(tip),
            metadatas={"user_id": user_id, "activated": 1}
        )
        print("Add_tip: ", tip, " ID: ", embedding_id, " user_id: ", user_id)

    def parse_expression(
        self,
        s: str
    ):
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
            result_list = expr.parseString(s)[0]
            return result_list
        except Exception as e:
            return -1

    async def add_data(
        self, 
        user_id: str,
        doc: str, 
    ):
        print("="*30)
        result = self.parse_expression(doc)
        if result == -1:
            await self.add_tip(
                user_id=user_id, tip=doc
            )
            return
        else:
            expression = [
                item.lower().replace('_',' ').replace('-',' ') 
                if len(item) > 1 else item for item in result
            ]
        key = expression[0]
        right_hand_size = expression[2:]
        for enum, entity in enumerate(right_hand_size,start=2):
            if len(entity) <= 1:
                continue
            related_keys = await self.get_related_key(
                user_id=user_id, 
                query_texts=entity, 
                extracts=['documents','distances','metadatas']
            )
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
                    key_name = filtered_keys[0][0]
                    doc_id = filtered_keys[0][1]['doc_id']
                    if key_name != entity:
                        expression[enum] = key_name
                    await self.add_key(user_id=user_id, key=key, doc_id=doc_id)
                    print("="*10)
        doc = str(expression)
        doc_id = deterministic_uuid(user_id+doc) + "-doc"
        await self.add_doc(
            user_id=user_id, document=doc
        )
        await self.add_key(
            user_id=user_id, key=key, doc_id=doc_id
        )        

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
                elif isinstance(extract_item[0], dict):
                    extracted_results[item] = ([extract_item[0]])
            else:
                extracted_results[item] = extract_item

        return extracted_results

    async def get_related_doc(
        self, 
        query_texts, 
        user_id: str = None,
        n_results=None, 
        extracts=None, 
    ) -> dict:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id:
            where_dict = {
                "user_id": {
                    "$eq": user_id
                }   
            }
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
        n_results=None, 
        extracts=None, 
    ) -> dict:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id:
            where_dict = {
                "$and": [
                    {
                        "user_id": {
                            "$eq": user_id
                        }   
                    },
                    {
                        "activated": {
                            "$eq": 1
                        }
                    }
                ]
            }
        else:
            where_dict = {
                "activated": {
                    "$eq": 1
                }
            }

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
        n_results=None, 
        extracts=None, 
    ) -> dict:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id:
            where_dict = {
                "$and": [
                    {
                        "user_id": {
                            "$eq": user_id
                        }   
                    },
                    {
                        "activated": {
                            "$eq": 1
                        }
                    }
                ]
            }
        else:
            where_dict = {
                "activated": {
                    "$eq": 1
                }
            }

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
                ids=[embedding_ids],
                where={
                    "user_id": {
                        "$eq": user_id
                    }   
                }
            )
            return result['documents'][0]
        elif isinstance(embedding_ids,list):
            ids_set = set(embedding_ids)
            if len(ids_set) == len(embedding_ids):
                result = await document_collection.get(
                    ids=embedding_ids,
                    where={
                        "user_id": {
                            "$eq": user_id
                        }   
                    }
                )
                return result['documents']
            else:
                distinct_ids = list(dict.fromkeys(embedding_ids))
                result = await document_collection.get(
                    ids=distinct_ids,
                    where={
                        "user_id": {
                            "$eq": user_id
                        }   
                    }
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
        extracts = None
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id:
            where_dict = {
                "user_id": {
                    "$eq": user_id
                }   
            }
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
        extracts = None
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id:
            where_dict = {
                "user_id": {
                    "$eq": user_id
                }   
            }
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
        extracts = None
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        if user_id:
            where_dict = {
                "user_id": {
                    "$eq": user_id
                }   
            }
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

    async def remove_data(
        self, 
        embedding_id: str | list,
    ) -> bool:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        ids = [embedding_id] if isinstance(embedding_id, str) else embedding_id
        for id in ids:
            if id.endswith("-key"):
                key_collection = await chroma_client.get_or_create_collection(
                    name="key",
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"},
                )
                await key_collection.delete(
                    ids=id
                )
            elif id.endswith("-doc"):
                document_collection = await chroma_client.get_or_create_collection(
                    name="document",
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"},
                )
                res = await document_collection.get(
                    ids=id
                )
                key_num = res['metadatas'][0]['key_num'] - 1
                if key_num == 0:
                    await document_collection.delete(
                        ids=id,
                    )
                else:
                    await document_collection.update(
                        ids=id,
                        metadatas={"key_num": key_num}
                    )
            elif id.endswith("-tip"):
                tip_collection = await chroma_client.get_or_create_collection(
                    name="tip",
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"},
                )
                await tip_collection.delete(
                    ids=id
                )
            else:
                raise Exception('The suffix of the embedding_id is incorrect.')
            
    async def clear_doc(
        self,
        user_id: str
    ):
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)
        key_collection = await chroma_client.get_or_create_collection(
            name="key",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        await key_collection.delete(
            where={
                "user_id": {
                    "$eq": user_id
                }   
            }
        )
        document_collection = await chroma_client.get_or_create_collection(
            name="document",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        await document_collection.delete(
            where={
                "user_id": {
                    "$eq": user_id
                }   
            }
        )
        tip_collection = await chroma_client.get_or_create_collection(
            name="tip",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        await tip_collection.delete(
            where={
                "user_id": {
                    "$eq": user_id
                }   
            }
        )

            
    async def update_activated(
        self, 
        embedding_id: str | list,
        activated: int,
    ) -> bool:
        chroma_client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)

        ids = [embedding_id] if isinstance(embedding_id, str) else embedding_id
        for id in ids:
            if id.endswith("-key"):
                key_collection = await chroma_client.get_or_create_collection(
                    name="key",
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"},
                )
                await key_collection.update(
                    ids=id,
                    metadatas={"activated": activated}
                )

            elif id.endswith("-tip"):
                tip_collection = await chroma_client.get_or_create_collection(
                    name="tip",
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"},
                )
                await tip_collection.update(
                    ids=id,
                    metadatas={"activated": activated}
                )

            else:
                raise Exception('The suffix of the embedding_id is incorrect.')