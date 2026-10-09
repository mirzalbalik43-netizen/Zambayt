"""Слой данных (CRUD-операции с SQLite)."""
import sqlite3
import os
from src.config import DB_PATH

def get_connection():
    """Возвращает новое соединение с БД SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализирует структуры таблиц базы данных."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processes (
        pid INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        owner TEXT NOT NULL,
        memory_used INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        content TEXT DEFAULT '',
        owner TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS syscalls_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        syscall_name TEXT NOT NULL,
        args TEXT,
        user TEXT,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        used INTEGER DEFAULT 0,
        limit_val INTEGER DEFAULT 1024
    )""")

    conn.commit()
    conn.close()

def execute_insert(table, data):
    """Универсальная вставка записи."""
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def execute_select(table, conditions=None):
    """Универсальная выборка записей."""
    sql = f"SELECT * FROM {table}"
    params = ()
    if conditions:
        where = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        sql += f" WHERE {where}"
        params = tuple(conditions.values())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return result

def execute_update(table, data, conditions):
    """Универсальное обновление записей."""
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(data.values()) + tuple(conditions.values()))
    conn.commit()
    conn.close()

def execute_delete(table, conditions=None):
    """Универсальное удаление записей."""
    conn = get_connection()
    cursor = conn.cursor()
    if not conditions:
        sql = f"DELETE FROM {table}"
        cursor.execute(sql)
    else:
        where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        cursor.execute(sql, tuple(conditions.values()))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[OK] База данных успешно инициализирована.")