import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(current_dir)
sys.path.append(ROOT_PATH)

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

# m.clear_doc()
# m.train_doc(path=os.path.join(ROOT_PATH,"rag/formulas.txt"))

# with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_train_text2sql.json')) as f:
#     data = json.load(f)
#     for item in data:
#         print("question: ", item["question"],
#               "\nsql: ", item["sql"],)
#         m.train(item["question"],item["sql"])

# with open(os.path.join("llama3.1_8b.txt"), "w") as txt_file:
#     with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_dev_text2sql.json')) as f:
#         data = json.load(f)
#         count = 1
#         for item in data:
#             if count == 30:
#                 break
#             try:
#                 message = {
#                     "question": item["question"],
#                     "extract": None,
#                     "sql": None,
#                     "schema": None,
#                     "evidence": None,
#                     "message_to": "extractor",
#                     "response": None,
#                     "sql_result": None
#                 }
#
#                 message = m.extractor.chat(message, m.llm)
#                 _, schema_str, evidence_str = m.filter.create_filter_prompt(message["entity"], "1", m.vectordb)
#
#                 print(
#                     "=" * 50 +
#                     "\nQuestion " + str(count) + ": " + str(message['question']) +
#                     "\nextract: " + str(message['entity']) +
#                     "\n" + "=" * 30 + "SCHEMA: \n" + schema_str +
#                     "\n" + "=" * 30 + "EVIDENCE: " + evidence_str +
#                     "\n\n",
#                 )
#                 print(
#                   "=" * 50 +
#                     "\nQuestion " + str(count) + ": " + str(message['question']) +
#                     "\nextract: " + str(message['entity']) +
#                     "\n" + "=" * 30 + "SCHEMA: \n" + schema_str +
#                     "\n" + "=" * 30 + "EVIDENCE: " + evidence_str +
#                     "\n\n",
#                   file=txt_file
#                 )
#             except Exception as e:
#                 print(e)
#             finally:
#                 count += 1

message = {
    "question": "What is the current ratio of China Construction Bank in millions of yuan?",
    "extract": None,
    "sql": None,
    "schema": None,
    "evidence": None,
    "message_to": "extractor",
    "response": None,
    "sql_result": None
}

message = m.extractor.chat(message=message, llm=m.llm, vectordb=m.vectordb)
message = m.filter.chat(message=message, llm=m.llm, vectordb=m.vectordb)
for k,v in message.items():
    print(k)
    print(v)