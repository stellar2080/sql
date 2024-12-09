import os

from src.manager.manager import Manager
from src.utils.data_rag import SCHEMA,DOCUMENT

ROOT_PATH = os.path.abspath("../")

m = Manager(
    config={
        'mode': 'train',
        'mapdb_path': os.path.join(ROOT_PATH,"db","map.sqlite3"),
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'client': 'http',
        'host': 'localhost',
        'port': '8000',
    },
)

# m.clear()
m.train(schema_list=SCHEMA)
m.train(doc_list=DOCUMENT)

# with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_train_text2sql.json')) as f:
#     data = json.load(f)
#     for item in data:
#         print("question: ", item["question"],
#               "\nsql: ", item["sql"],)
#         m.train(item["question"],item["sql"])

