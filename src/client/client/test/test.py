import asyncio
import datetime
import json
import os
import pandas as pd
import sys

# current_dir = os.path.dirname(os.path.abspath(__file__))
# CLIENT_PATH = os.path.dirname(os.path.dirname(current_dir))
# sys.path.append(CLIENT_PATH)
# from client.manager.manager import Manager

# manager = Manager(
#     config={
#         'user_id': '1',
#         'platform': 'Tongyi',
#         'model': 'deepseek-v3',
#         'api_key': "sk-9536a97947b641ad9e287da238ba3abb",
#         'target_db_path': os.path.join(CLIENT_PATH,"dataset","Bank_Financials.sqlite"),
#         'vectordb_host': 'localhost',
#         'vectordb_port': '8000',
#         'MAX_ITERATIONS': 3,
#         'DO_SAMPLE': False,
#         'TEMPERATURE': 0.1,
#         'TOP_P': 0.1,
#         'MAX_TOKENS': 8192,
#         'N_RESULTS': 3,
#         'E_HINT_THRESHOLD': 0.30,
#         'E_COL_THRESHOLD': 0.30,
#         'E_VAL_THRESHOLD': 0.30,
#         'E_COL_STRONG_THRESHOLD': 0.48,
#         'E_VAL_STRONG_THRESHOLD': 0.48,
#         'F_HINT_THRESHOLD': 0.80,
#         'F_COL_THRESHOLD': 0.60,
#         'F_LSH_THRESHOLD': 0.40,
#         'F_VAL_THRESHOLD': 0.60,
#         'F_COL_STRONG_THRESHOLD': 0.85,
#         'F_VAL_STRONG_THRESHOLD': 0.85,
#         'G_HINT_THRESHOLD': 0.30,
#     },
# )

# # # with open(os.path.join(CLIENT_PATH,"knowledge","repository.txt"),mode='r',encoding='utf-8') as f:
# # #     for line in f:
# # #         manager.add_to_vectordb(line.strip(),'repository.txt')
        
# # # with open(os.path.join(ROOT_PATH,'dataset','Bank_Financials_dev_proc.json')) as f:
# # #     data = json.load(f)
# # #     for i in range(0, 40):
# # #         item = data[i]
# # #         try:
# # #             print("="*50)
# # #             question = item['question'] 
# # #             message = manager.chat(question)
# # #             print("="*30)
# # #             print(question)
# # #             print(message['sql'])
# # #             print(message['sql_result'])
# # #             print("="*30)
# # #             query = item['query']
# # #             cur = manager.db_conn.cursor()
# # #             cur.execute(query)
# # #             result = cur.fetchall()
# # #             print(question)
# # #             print(query)
# # #             print(result)
# # #             print("="*50)
# # #         except Exception as e:
# # #             print(e)

# async def test(manager: Manager):
#     message = {
#         "question": "I want the current ratio of all bank",
#         "entity": None,
#         "dialect": "sqlite",
#         "schema": None,
#         "hint": None,
#         "sql": None,
#         "sql_result": None,
#         "message_to": "extractor"
#     }
#     message = await manager.chat(message=message)
#     print(message['sql'])
#     print(message['sql_result'])

async def test():
    yield 1
    await asyncio.sleep(5)
    yield 2
    yield 3

async def test2():
    model = test
    async for value in model():
        print(value)

if __name__ == '__main__':
    asyncio.run(test2())