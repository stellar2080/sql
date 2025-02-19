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

with open(os.path.join("output.txt"), "w") as txt_file:
    with open(os.path.join(ROOT_PATH,'dataset','Bank_Financials_dev.json')) as f:
        data = json.load(f)
        count = 1
        for item in data:
            if count == 10:
                break
            try:
                message = {
                    "question": item["question"],
                    "extract": None,
                    "sql": None,
                    "schema": None,
                    "hint": None,
                    "message_to": "extractor",
                    "response": None,
                    "sql_result": None
                }

                message = m.extractor.chat(message, m.llm, m.vectordb)
                # _, schema_str, hint_str = m.filter.create_filter_prompt(message["entity"], "1", m.vectordb)

                print(
                    "=" * 50 +
                    "\nQuestion " + str(count) + ": " + str(message['question']) +
                    "\nextract: " + str(message['entity']) +
                    "\n\n",
                )
                print(
                  "=" * 50 +
                    "\nQuestion " + str(count) + ": " + str(message['question']) +
                    "\nextract: " + str(message['entity']) +
                    "\n\n",
                  file=txt_file
                )
            except Exception as e:
                print(e)
            finally:
                count += 1

# message = {
#     "question": None,
#     "extract": None,
#     "sql": None,
#     "schema": None,
#     "hint": None,
#     "message_to": "extractor",
#     "response": None,
#     "sql_result": None
# }

# if __name__ == '__main__':
#     message = m.extractor.chat(message=message, llm=m.llm, vectordb=m.vectordb)
#     # message = m.filter.chat(message=message, llm=m.llm, vectordb=m.vectordb)