import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(current_dir)
sys.path.append(ROOT_PATH)
from src.utils.utils import get_cos_similarity, get_embedding, parse_json, user_message
from src.manager.manager import Manager
import spacy

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
#     for i in range(0, 10):
#         item = data[i]
#         try:
#             question = item['question'] 
#             message = manager.chat(question) 
#             print("="*50)
#             print(message['question'])
#             print(message['sql'])
#             print(message['sql_result'])
#             # query = item['query']
#             # cur = manager.db_conn.cursor()
#             # cur.execute(query)
#             # result = cur.fetchall()
#             # print("="*50)
#             # print(question)
#             # print(query)
#             # print(result)
#         except Exception as e:
#             print(e)

message = {
    "question": "What is the total amount of due from interbank deposits and borrowings from other financial institutions for each bank?",
    "entity": None,
    "dialect": "sqlite",
    "schema": None,
    "hint": None,
    "sql": None,
    "sql_result": None,
    "message_to": "extractor"
}

if __name__ == '__main__':
#     # message = manager.extractor.chat(message=message, llm=manager.llm, vectordb=manager.vectordb, db_conn=manager.db_conn)
#     # message = manager.filter.chat(message=message, llm=manager.llm, vectordb=manager.vectordb, db_conn=manager.db_conn)
#     # message = manager.generator.chat(message=message, llm=manager.llm)
#     # message = manager.reviser.chat(message=message, llm=manager.llm, db_conn=manager.db_conn)
    message = manager.chat(message=message)
    print(message['sql_result'])