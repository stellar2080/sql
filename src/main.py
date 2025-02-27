import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(current_dir)
sys.path.append(ROOT_PATH)
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

# manager.add_doc_to_vectordb(os.path.join(ROOT_PATH,"repository.txt"))
        
# with open(os.path.join(ROOT_PATH,'dataset','Bank_Financials_dev_proc.json')) as f:
#     data = json.load(f)
#     for i in range(20, 30):
#         item = data[i]
#         try:
#             print("="*50)
#             question = item['question'] 
#             message = manager.chat(question) 
#             print(question)
#             print(message['sql'])
#             print(message['sql_result'])
#             print("="*30)
#             query = item['query']
#             cur = manager.db_conn.cursor()
#             cur.execute(query)
#             result = cur.fetchall()
#             print(question)
#             print(query)
#             print(result)
#             print("="*50)
#         except Exception as e:
#             print(e)

message = {
    "question": "Which banks have a positive net interest income?",
    "entity": None,
    "dialect": "sqlite",
    "schema": None,
    "hint": None,
    "sql": None,
    "sql_result": None,
    "message_to": "extractor"
}

if __name__ == '__main__':
    # message = manager.extractor.chat(message=message, llm=manager.llm, vectordb=manager.vectordb, db_conn=manager.db_conn)
    # message = manager.filter.chat(message=message, llm=manager.llm, vectordb=manager.vectordb, db_conn=manager.db_conn)
    # message = manager.generator.chat(message=message, llm=manager.llm)
    # message = manager.reviser.chat(message=message, llm=manager.llm, db_conn=manager.db_conn)
    message = manager.chat(message=message)
    print(message['sql'])
    print(message['sql_result'])