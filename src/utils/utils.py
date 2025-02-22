import difflib
import functools
import hashlib
import queue
import threading
import time
import uuid
from typing import Union
import json
from datasketch import MinHash, MinHashLSH
import ast
import numpy as np
from chromadb.utils import embedding_functions

from src.utils.const import F_LSH_THRESHOLD

def system_message(message: str):
    return {'role': 'system', 'content': message}

def user_message(message: str):
    return {'role': 'user', 'content': message}

def assistant_message(message: str):
    return {'role': 'assistant', 'content': message}

def get_response_content(response, platform):
    if platform == "Qwen":
        return response.output.choices[0].message.content
    elif platform == "Ollama":
        return response.message.content
    elif platform == "Api":
        return response['response']

def deterministic_uuid(content: Union[str, bytes]) -> str:
    if isinstance(content, str):
        content_bytes = content.encode("utf-8")
    elif isinstance(content, bytes):
        content_bytes = content
    else:
        raise ValueError("Content type is not supported: {}".format(type(content)))
    hash_object = hashlib.sha256(content_bytes)
    hash_hex = hash_object.hexdigest()
    namespace = uuid.UUID("00000000-0000-0000-0000-000000000000")
    content_uuid = str(uuid.uuid5(namespace, hash_hex))

    return content_uuid

def parse_json(text: str):
    try:
        start = text.rfind("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            json_string = text[start: end+1]
            json_data = json.loads(json_string)
            return json_data
        else:
            raise Exception('parse json error!\n')
    except Exception as e:
        print(e)

def parse_sql(text: str) -> str:
    try:
        start = text.rfind("```sql")
        end = text.rfind("```", start + 6)

        if start != -1 and end != -1:
            sql_string = text[start + 7: end]
            return sql_string
        else:
            raise Exception("parse sql error!\n")
    except Exception as e:
        print(e)

def parse_list(text):
    try:
        start = text.rfind('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            return ast.literal_eval(text[start:end+1])
        else:
            raise Exception("parse list error!\n")
    except Exception as e:
        print(e)

def show_perf(func):
    def wrapper(*args, **kwargs):
        print('*' * 20)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'{func.__name__} Cost: {time.perf_counter() - start}')
        return result
    return wrapper

def timeout(time_args):
    def _timeout(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            q = queue.Queue(maxsize=1)
            def run():
                try:
                    result = func(*args, **kwargs)
                    q.put((result,None))
                except Exception as e:
                    exception = e
                    q.put((None,exception))
            thread = threading.Thread(target=run)
            thread.start()
            thread.join(time_args)
            if thread.is_alive():
                raise Exception("Function call timed out.")
            result, exception = q.get()
            if exception:
                raise exception
            return result
        return wrapper
    return _timeout

def lsh(query_list: list, target_list: list) -> dict:

    query_results = {}

    lsh = MinHashLSH(threshold=F_LSH_THRESHOLD, num_perm=128)
    n_gram = 3

    for i, target in enumerate(target_list):
        minhash = MinHash(num_perm=128)
        target = target.lower().replace(' ', '').replace('_', '').replace('-','').rstrip('s')
        grams = [target[j:j+n_gram] for j in range(len(target) - n_gram + 1)]
        for gram in grams:
            minhash.update(gram.encode('utf-8'))
        lsh.insert(i, minhash)

    for query_str in query_list:
        query_minhash = MinHash(num_perm=128)
        query_str_copy = query_str.lower().replace(' ', '').replace('_', '').replace('-','').rstrip('s')
        query_grams = [query_str_copy[j:j+n_gram] for j in range(len(query_str_copy) - n_gram + 1)]
        for gram in query_grams:
            query_minhash.update(gram.encode('utf-8'))

        idx_list = lsh.query(query_minhash)
        if len(idx_list) > 0:
            query_results[query_str] = [target_list[idx] for idx in idx_list]

    return query_results

def get_subsequence_similarity(entity1, entity2):
    entity1 = entity1.lower().replace(' ', '').replace('_', '').replace('-','').rstrip('s')
    entity2 = entity2.lower().replace(' ', '').replace('_', '').replace('-','').rstrip('s')
    return difflib.SequenceMatcher(None, entity1, entity2).ratio()

def get_cos_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)

    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    return dot_product / (norm_vec1 * norm_vec2)

def get_embedding(_str: str):
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    return embedding_func([_str.lower().replace('_',' ').replace('-',' ')])[0]

def get_embedding_list(_list: list):
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    return embedding_func([item.lower().replace('_',' ').replace('-',' ') for item in _list])