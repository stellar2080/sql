import json
import os

from src.manager.manager import Manager
from src.utils.utils import user_message

ROOT_PATH = os.path.abspath("../")
os.environ["DASHSCOPE_API_KEY"] = "sk-9536a97947b641ad9e287da238ba3abb"

m = Manager(
    config={
        # 'platform': 'Qwen',
        # 'model': 'qwen-max',
        'platform': 'Ollama',
        'model': 'llama3.1:8b',
        'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'vectordb_client': 'http',
        'vectordb_host': 'localhost',
        'vectordb_port': '8000'
    },
)

# m.clear_doc()
# m.train_doc(path="../rag/formulas.txt")
# with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_train_text2sql.json')) as f:
#     data = json.load(f)
#     for item in data:
#         print("question: ", item["question"],
#               "\nsql: ", item["sql"],)
#         m.train(item["question"],item["sql"])


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


with open(os.path.join("output.txt"), "w") as txt_file:
    with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_dev_text2sql.json')) as f:
        data = json.load(f)
        count = 1
        for item in data:
            message = {
                "question": item["question"],
                "extract": None,
                "sql": None,
                "schema": None,
                "evidence": None,
                "message_to": "extractor",
                "response": None,
                "sql_result": None
            }

            message = m.extractor.chat(message, m.llm)
            _, schema_str, evidence_str = m.filter.create_filter_prompt(message["extract"], "1", m.vectordb)

            print(
                "=" * 50 +
                "\nQuestion " + str(count) + ": " + str(message['question']) +
                "\nextract: " + str(message['extract']) +
                "\n" + "=" * 30 + "SCHEMA: \n" + schema_str +
                "\n" + "=" * 30 + "EVIDENCE: " + evidence_str +
                "\n\n",
            )
            print(
              "=" * 50 +
                "\nQuestion " + str(count) + ": " + str(message['question']) +
                "\nextract: " + str(message['extract']) +
                "\n" + "=" * 30 + "SCHEMA: \n" + schema_str +
                "\n" + "=" * 30 + "EVIDENCE: " + evidence_str +
                "\n\n",
              file=txt_file
            )
            count += 1