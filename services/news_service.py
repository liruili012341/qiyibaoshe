import datetime
from db import get_db_connection, dump_json

def save_news_to_db(filename, title, timestamp, files_info):
    """保存新闻记录到数据库"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO news (id, title, date, timestamp, media_files) VALUES (?, ?, ?, ?, ?)',
        (filename, title, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), timestamp, dump_json(files_info)),
    )
    conn.commit()
    conn.close()