import os.path
import sqlite3

from src.utils.utils import info


class MapDB(object):
    def __init__(self,config):
        self.conn = None
        if not os.path.exists(config["mapdb_path"]):
            info("Mapdb_path {} is not exists.".format(config["mapdb_path"]))
        else:
            self.conn = sqlite3.connect(config["mapdb_path"])

    def add_doc(
        self,
        embedding_id: str,
        document: str
    ):
        if self.conn is None:
            info("MapDB connection failed.")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO id_table (embedding_id) VALUES (?)", (embedding_id,))
        cursor.execute("INSERT INTO doc_table (document) VALUES (?)", (document,))
        cursor.close()
        self.conn.commit()

    def get_doc(
        self,
        embedding_id: str,
    ):
        if self.conn is None:
            info("MapDB connection failed.")
        cursor = self.conn.cursor()
        cursor.execute("SELECT document FROM id_table it, doc_table dt WHERE it.document_id = dt.document_id AND embedding_id=?", (embedding_id,))
        content = str(cursor.fetchall()[0][0])
        cursor.close()
        return content

    def clear(self):
        if self.conn is None:
            info("MapDB connection failed.")
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS id_table")
        cursor.execute("CREATE TABLE IF NOT EXISTS id_table (document_id INTEGER PRIMARY KEY AUTOINCREMENT, embedding_id TEXT)")
        cursor.execute("DROP TABLE IF EXISTS doc_table")
        cursor.execute("CREATE TABLE IF NOT EXISTS doc_table (document_id INTEGER PRIMARY KEY AUTOINCREMENT, document TEXT)")
        cursor.close()