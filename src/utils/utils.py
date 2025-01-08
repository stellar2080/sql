import hashlib
import uuid
from typing import Union
import json
from typing import Dict

def system_message(message: str):
    return {'role': 'system', 'content': message}

def user_message(message: str):
    return {'role': 'user', 'content': message}

def assistant_message(message: str):
    return {'role': 'assistant', 'content': message}

def get_res_content(response):
    return response.output.choices[0].message.content

def get_res_finish_reason(response):
    return response.output.choices[0].finish_reason

def get_res_tool_calls(response):
    return response.output.choices[0].message.tool_calls

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
            print(f"parse json error!\n")
            print(f"json_string: {json_string}\n\n")
            pass

    return text

def check_filter_response(json_data: Dict) -> bool:
    FLAGS = ['keep_all', 'drop_all']
    for k, v in json_data.items():
        if isinstance(v, str):
            if v not in FLAGS:
                print(f"invalid table flag: {v}\n")
                print(f"json_data: {json_data}\n\n")
                return False
        elif isinstance(v, list):
            pass
        else:
            print(f"invalid flag type: {v}\n")
            print(f"json_data: {json_data}\n\n")
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
            print(f"parse sql error!\n")
            return ""
    except Exception as e:
        print(e)
        pass
