import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(current_dir)
sys.path.append(ROOT_PATH)
from src.utils.utils import get_cos_similarity, get_embedding, parse_json, user_message
from src.manager.manager import Manager

os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"

manager = Manager(
    config={
        'platform': 'Api',
        'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'vectordb_client': 'http',
        'vectordb_host': 'localhost',
        'vectordb_port': '8000'
    },
)

# with open(os.path.join(ROOT_PATH,'dataset','Bank_Financials_dev.json')) as f:
#     data = json.load(f)
#     for i in range(50):
#         item = data[i]
#         try:
#             # message = {
#             #     "question": item["question"],
#             #     "extract": None,
#             #     "sql": None,
#             #     "schema": None,
#             #     "hint": None,
#             #     "message_to": "extractor",
#             #     "sql_result": None
#             # }
#             message = manager.chat(item["question"])
#         except Exception as e:
#             print(e)

message = {
    "question": "Find the banks where precious metal assets account for more than 0.5% of total assets.",
    "entity": None,
    "dialect": "sqlite",
    "schema": None,
    "hint": None,
    "sql": None,
    "sql_result": None,
    "message_to": "extractor"
}

if __name__ == '__main__':
    message = manager.extractor.chat(message=message, llm=manager.llm, vectordb=manager.vectordb, db_conn=manager.db_conn)
    message = manager.filter.chat(message=message, llm=manager.llm, vectordb=manager.vectordb, db_conn=manager.db_conn)
    message = manager.decomposer.chat(message=message, llm=manager.llm)
    message = manager.reviser.chat(message=message, llm=manager.llm, db_conn=manager.db_conn)