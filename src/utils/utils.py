import hashlib
import uuid
from typing import Union
import json
from typing import Dict

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

def parse_json(text: str) -> dict:
    start = text.rfind("```json")
    end = text.rfind("```", start + 7)

    if start != -1 and end != -1:
        json_string = text[start + 7: end]

        try:
            json_data = json.loads(json_string)
            valid = check_filter_response(json_data)
            if valid:
                return json_data
            else:
                return {}
        except:
            info(f"parse json error!\n")
            info(f"json_string: {json_string}\n\n")
            pass

    return {}

def check_filter_response(json_data: Dict) -> bool:
    FLAGS = ['keep_all', 'drop_all']
    for k, v in json_data.items():
        if isinstance(v, str):
            if v not in FLAGS:
                info(f"invalid table flag: {v}\n")
                info(f"json_data: {json_data}\n\n")
                return False
        elif isinstance(v, list):
            pass
        else:
            info(f"invalid flag type: {v}\n")
            info(f"json_data: {json_data}\n\n")
            return False
    return True

def parse_sql(text: str) -> str:
    try:
        start = text.rfind("```sql")
        end = text.rfind("```", start + 6)

        if start != -1 and end != -1:
            sql_string = text[start + 7: end]
            return sql_string
        else:
            info(f"parse sql error!\n")
            return ""
    except Exception as error:
        print(error)
        pass

def extract_documents(query_results) -> list:
    if query_results is None:
        return []
    print(query_results)
    if "documents" in query_results:
        documents = query_results["documents"]

        if len(documents) == 1 and isinstance(documents[0], list):
            try:
                documents = [json.loads(doc) for doc in documents[0]]
            except Exception as e:
                return documents[0]

        return documents

def extract_embedding_ids(query_results) -> list:
    if query_results is None:
        return []
    if "ids" in query_results:
        ids = query_results["ids"]

        if len(ids) == 1 and isinstance(ids[0], list):
            try:
                ids = [json.loads(doc) for doc in ids[0]]
            except Exception as e:
                return ids[0]

        return ids

def info(message: str):
    print("[INFO]:",message)

def system_message(message: str):
    return {'role': 'system', 'content': message}

def user_message(message: str):
    return {'role': 'user', 'content': message}

def assistant_message(message: str):
    return {'role': 'assistant', 'content': message}