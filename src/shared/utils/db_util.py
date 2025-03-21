import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union

from config import DB_TIMEOUT


def execute(db_path, query: str, params: Union[Tuple, List[Tuple]] = (), many: bool = False) -> None:
    with sqlite3.connect(db_path, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)
        conn.commit()

def run_script(db_path: str, script: str) -> None:
    with sqlite3.connect(db_path, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.executescript(script)
        conn.commit()

def fetch_all(db_path, query: str, params: Tuple = ()) -> List[Tuple]:
    with sqlite3.connect(db_path, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def fetch_one(db_path, query: str, params: Tuple = ()) -> Optional[Tuple]:
    with sqlite3.connect(db_path, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

def init_db(db_path, schema_sql: str):
    if not os.path.exists(db_path):
        with open(db_path, 'w'):
            pass

    execute(db_path, "PRAGMA journal_mode=WAL;")
    run_script(db_path, schema_sql)

def insert_dict(db_path, table: str, data: Dict[str, Any]) -> None:
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    values = tuple(data.values())
    query = f"INSERT OR IGNORE INTO {table} ({keys}) VALUES ({placeholders})"
    execute(db_path, query, values)

def insert_batch_dicts(db_path, table: str, data_list: List[Dict[str, Any]]) -> None:
    if not data_list:
        return
    keys = data_list[0].keys()
    keys_str = ', '.join(keys)
    placeholders = ', '.join(['?'] * len(keys))
    values = [tuple(d.values()) for d in data_list]
    query = f"INSERT OR IGNORE INTO {table} ({keys_str}) VALUES ({placeholders})"
    execute(db_path, query, values, many=True)