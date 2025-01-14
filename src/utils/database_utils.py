import os
import sqlite3
from urllib.parse import urlparse

import requests


def connect_to_sqlite(
    url: str,
    check_same_thread: bool = False,
    **kwargs
):
    if not os.path.exists(url):
        path = os.path.basename(urlparse(url).path)
        response = requests.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
    conn = sqlite3.connect(
        url,
        check_same_thread=check_same_thread,
        **kwargs
    )
    dialect = "SQLite"
    return conn,dialect