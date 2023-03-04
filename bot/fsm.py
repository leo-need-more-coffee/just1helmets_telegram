import logging
import sqlite3
import json
import logging
import secrets
import random
from hashlib import sha256, md5

db_name = "FSM.db"

class State:
    def __init__(self, chat_id:int, state:str, data:dict={}):
        self.chat_id:int = chat_id
        self.state:str = state
        self.data:str = data

    def set(chat_id:int, state:str, data:dict={}):
        conn = sqlite3.connect(db_name)
        if not State.get(chat_id):
            conn.execute("INSERT INTO states (chat_id, state, data) \
                VALUES (?, ?, ?)", (chat_id, state, json.dumps(data)))
        else:
            conn.execute("UPDATE states SET chat_id = ?, state = ?, data = ? WHERE chat_id == ?",
                [chat_id, state, json.dumps(data), chat_id])
        conn.commit()
        conn.close()
        return State(chat_id, state, data)


    def delete(self):
        conn = sqlite3.connect(db_name)
        conn.execute("DELETE FROM states\
                WHERE chat_id == ?", [self.chat_id])
        conn.commit()
        conn.close()


    def get(chat_id):
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT chat_id, state, data FROM states WHERE chat_id==?", [chat_id])
        rows = cursor.fetchall()
        if len(rows) == 0:
            return None
        chat_id, state, data = rows[0]
        row = State(chat_id, state, json.loads(data) if data else {})    
        conn.close()
        return row

