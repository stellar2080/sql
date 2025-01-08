import os
import sqlite3


ROOT_PATH = os.path.abspath("../../")
conn = sqlite3.connect(os.path.join(ROOT_PATH,"dataset","Bank_Financials.sqlite"))
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tbl_names = cur.fetchall()
cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
sql_datas = cur.fetchall()

cols = []
for tbl_name in tbl_names:
    cur.execute(f"PRAGMA table_info('{tbl_name[0]}')")
    col_datas = cur.fetchall()
    cols = [[col_data[1],col_data[2]] for col_data in col_datas]
    sql_str: str = sql_datas[tbl_names.index(tbl_name)][0]
    start = 0
    num = 0
    while True:
        idx = sql_str.find("-- ", start)
        if idx == -1:
            break
        else:
            end = sql_str.find("\n", idx)
            start = end + 2
            sub_str = sql_str[idx + 3:end]
            Samples_idx = sub_str.find("Samples:")
            cols[num].append(sub_str if Samples_idx == -1 else sub_str[:Samples_idx-1])
            num += 1
    print(cols)
