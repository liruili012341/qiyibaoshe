import json
import sqlite3
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from config import DB_FILE

ph = PasswordHasher()


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
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        '''
    )
    
    # 添加用户表
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        '''
    )
    
    # 添加点赞表
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            news_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (news_id) REFERENCES news (id),
            UNIQUE (user_id, news_id)
        )
        '''
    )
    
    # 添加登录尝试表
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            username TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_attempt TEXT NOT NULL,
            locked_until TEXT,
            UNIQUE (ip_address, username)
        )
        '''
    )
    
    # 检查是否存在管理员账号，如果不存在则创建默认管理员
    cur.execute('SELECT COUNT(*) FROM admin')
    count = cur.fetchone()[0]
    if count == 0:
        # 创建默认管理员账号，使用Argon2id加密
        default_username = 'admin'
        default_password = 'admin123'
        # 对用户名和密码进行Argon2id加密
        hashed_username = ph.hash(default_username)
        hashed_password = ph.hash(default_password)
        cur.execute(
            'INSERT INTO admin (username, password) VALUES (?, ?)',
            (hashed_username, hashed_password)
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
