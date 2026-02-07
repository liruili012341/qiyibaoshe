import json
import sqlite3
from config import DB_FILE


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            media_files TEXT NOT NULL DEFAULT '[]'
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS comments (
            news_id TEXT PRIMARY KEY,
            comments_json TEXT NOT NULL DEFAULT '[]'
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            link TEXT NOT NULL
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS discuss (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT
        )
        '''
    )
    conn.commit()
    conn.close()


def dump_json(value):
    return json.dumps(value, ensure_ascii=False)


def load_json(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default
