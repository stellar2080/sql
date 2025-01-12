import os

from src.manager.manager import Manager

ROOT_PATH = os.path.abspath("../")

m = Manager(
    config={
        'mode': 'train',
        'vectordb_path': os.path.join(ROOT_PATH, 'vectordb'),
        'vectordb_client': 'http',
        'vectordb_host': 'localhost',
        'vectordb_port': '8000',
    },
)

# m.clear_rag()

# m.train_doc(path="../rag/formulas.txt")

# with open(os.path.join(ROOT_PATH,'dataset','sft_bank_financials_train_text2sql.json')) as f:
#     data = json.load(f)
#     for item in data:
#         print("question: ", item["question"],
#               "\nsql: ", item["sql"],)
#         m.train(item["question"],item["sql"])