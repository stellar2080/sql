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

def parse_json(text: str):
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
                return text
        except:
            error(f"parse json error!\n")
            error(f"json_string: {json_string}\n\n")
            pass

    return text

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
            error(f"invalid flag type: {v}\n")
            error(f"json_data: {json_data}\n\n")
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
            error(f"parse sql error!\n")
            return ""
    except Exception as e:
        error(e)
        pass

def extract_query_results(query_results,extract: str) -> list:
    if query_results is None:
        return []
    info(query_results)
    if extract != 'documents' and extract != 'ids' and extract != 'metadatas':
        raise ValueError("Extract type is not supported.")
    if extract in query_results:
        extracts = query_results[extract]

        if len(extracts) == 1 and isinstance(extracts[0], list):
            try:
                extracts = [json.loads(doc) for doc in extracts[0]]
            except Exception as e:
                return extracts[0]

        return extracts


def info(message):
    print("[INFO]:",end="")
    print(message)

def error(message):
    print("[ERROR]:",end="")
    print(message)


def system_message(message: str):
    return {'role': 'system', 'content': message}

def user_message(message: str):
    return {'role': 'user', 'content': message}

def assistant_message(message: str):
    return {'role': 'assistant', 'content': message}

def get_memory_str(role: list,memory: list) -> str:
    memory_dict = {role[0]: memory[0], role[1]: memory[1]}
    return json.dumps(memory_dict)

def get_res_content(response):
    return response.output.choices[0].message.content

def get_res_finish_reason(response):
    return response.output.choices[0].finish_reason

def get_res_tool_calls(response):
    return response.output.choices[0].message.tool_calls

def schema_list_to_str(schema_list):
    schema_str = ""
    for schema in schema_list:
        schema_str += "=====" + schema
    return schema_str