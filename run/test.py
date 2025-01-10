import json
import os

from src.manager.manager import Manager

ROOT_PATH = os.path.abspath("../")
os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"

m = Manager(
    config={
        'platform': 'Qwen',
        'model': 'qwen-max',
        'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'vectordb_client': 'http',
        'vectordb_host': 'localhost',
        'vectordb_port': '8000'
    },
)

# with open(os.path.join("output.txt"), "w") as txt_file:
#     with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_dev_text2sql.json')) as f:
#         data = json.load(f)
#         count = 1
#         for item in data:
#             info("Question " + str(count))
#             count += 1
#
#             question = item["question"]
#             message = m.chat_nl2sql(question=question)
#             sql_0 = item["sql"]
#             result_0 = m.reviser.run_sql(sql_0)
#             sql_1 = message['sql']
#             result_1 = message['result']
#
#             print(
#               "Question: "+ question +
#               "\nSQL_0: " + sql_0 +
#               "\nSQL_1: " + sql_1 +
#               "\nRESULT_0: " + str(result_0) +
#               "\nRESULT_1: " + str(result_1) +
#               "\n\n",
#               file=txt_file
#             )

# m.chat("how many companies?")