import os

from src.manager.manager import Manager
from src.utils.data_rag import SCHEMA,DOCUMENT

ROOT_PATH = os.path.abspath("../")
os.environ["DASHSCOPE_API_KEY"] = "sk-6189784a69b24e53b99310316a1de2fc"

m = Manager(
    config={
        'platform': 'Qwen',
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

