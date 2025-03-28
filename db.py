# db.py

import sqlite3
import json

DB_PATH = "assistants.db"
VECTOR_STORE_MAP_FILE = "vector_store_map.json"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assistants (
            name TEXT PRIMARY KEY,
            openai_id TEXT,
            vector_store_id TEXT,
            prompt TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_assistants():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM assistants ORDER BY name")
    assistants = [row[0] for row in cursor.fetchall()]
    conn.close()
    return assistants

def get_assistant_details(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT openai_id, vector_store_id, prompt FROM assistants WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"id": result[0], "vector_store_id": result[1], "prompt": result[2]}
    return {}

def update_assistant(name, new_prompt, new_vector_store_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE assistants
        SET prompt = ?, vector_store_id = ?
        WHERE name = ?
    """, (new_prompt, new_vector_store_id, name))
    conn.commit()
    conn.close()

def load_vector_store_map():
    with open(VECTOR_STORE_MAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_vector_store_name(store_id):
    mapping = load_vector_store_map()
    return mapping.get(store_id, store_id)

def get_vector_store_id_from_name(name):
    mapping = load_vector_store_map()
    reversed_map = {v: k for k, v in mapping.items()}
    return reversed_map.get(name, name)
