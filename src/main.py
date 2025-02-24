import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(current_dir)
sys.path.append(ROOT_PATH)
from src.utils.utils import get_cos_similarity, get_embedding, parse_json, user_message
from src.manager.manager import Manager

os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"

m = Manager(
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
#     for i in range(5):
#         item = data[i]
#         try:
#             message = {
#                 "question": item["question"],
#                 "extract": None,
#                 "sql": None,
#                 "schema": None,
#                 "hint": None,
#                 "message_to": "extractor",
#                 "sql_result": None
#             }
#             message = m.extractor.chat(message, m.llm, m.vectordb)
#         except Exception as e:
#             print(e)

message = {
    "question": "What are the company names?",
    "entity": None,
    "dialect": "sqlite",
    "schema": None,
    "hint": None,
    "sql": None,
    "sql_result": None,
    "message_to": "extractor"
}

if __name__ == '__main__':
    message = m.extractor.chat(message=message, llm=m.llm, vectordb=m.vectordb, db_conn=m.db_conn)
    message = m.filter.chat(message=message, llm=m.llm, vectordb=m.vectordb, db_conn=m.db_conn)
    message = m.decomposer.chat(message=message, llm=m.llm)
    message = m.reviser.chat(message=message, llm=m.llm, db_conn=m.db_conn)
