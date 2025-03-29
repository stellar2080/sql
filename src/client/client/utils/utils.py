import asyncio
from collections import defaultdict
import difflib
import functools
import hashlib
import queue
import re
import threading
import time
import uuid
from typing import Union
import json
import ast
import numpy as np
from chromadb.utils import embedding_functions

def system_message(message: str):
    return {'role': 'system', 'content': message}

def user_message(message: str):
    return {'role': 'user', 'content': message}

def assistant_message(message: str):
    return {'role': 'assistant', 'content': message}

def get_response_content(response, platform):
    if platform == "Tongyi":
        return response.choices[0].message.content
    elif platform == "Custom":
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

def merge_duplicates(pairs):
    merged = defaultdict(list)
    for key, value in pairs:
        merged[key].extend(value)
    merged[key] = list(dict.fromkeys(merged[key]))
    return dict(merged)

def parse_json(text: str):
    try:
        start = text.rfind("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            json_string = text[start: end+1]
            json_data = json.loads(s=json_string, object_pairs_hook=merge_duplicates)
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

async def get_embedding_list(element_list: list):
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(
        None,
        embedding_func,
        [item.lower().replace('_', ' ').replace('-', ' ') for item in element_list]
    )
    return embeddings

def is_valid_ipv4(ip):
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None

def is_float(s):
    pattern = r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'
    return bool(re.match(pattern, s))