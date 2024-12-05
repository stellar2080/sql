import os

from src.manager.manager import Manager
from src.utils.const import GLM_API_KEY, QWEN_API_KEY
from src.utils.data_rag import SCHEMA,DOCUMENT

ROOT_PATH = os.path.abspath("../")

m = Manager(
    config={
        'api_key': QWEN_API_KEY,
        'llm': 'Qwen',
        'model': 'qwen-plus',
        'db_path': os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"),
        'mapdb_path': os.path.join(ROOT_PATH,"db","map.sqlite3"),
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'client': 'http',
        'host': 'localhost',
        'port': '8000'
    },
)

m.clear()
m.train(schema_list=SCHEMA)
m.train(doc_list=DOCUMENT)

# with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_train_text2sql.json')) as f:
#     data = json.load(f)
#     for item in data:
#         print("question: ", item["question"],
#               "\nsql: ", item["sql"],)
#         m.train(item["question"],item["sql"])

