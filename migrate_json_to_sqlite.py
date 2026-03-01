"""将旧的 JSON 数据迁移到 SQLite。"""
import argparse
import json
import os

from db import dump_json, get_db_connection, init_db


def load_json_file(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def migrate(data_file='data.json', comments_file='comments.json', ads_file='ads.json', discuss_file='discuss.json', clear=False):
    init_db()
    conn = get_db_connection()

    if clear:
        conn.execute('DELETE FROM news')
        conn.execute('DELETE FROM comments')
        conn.execute('DELETE FROM ads')
        conn.execute('DELETE FROM discuss')
        conn.commit()

    data_store = load_json_file(data_file, {'news': []})
    for item in data_store.get('news', []):
        conn.execute(
            '''
            INSERT OR REPLACE INTO news (id, title, date, timestamp, media_files)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                item.get('id'),
                item.get('title', ''),
                item.get('date', ''),
                item.get('timestamp', ''),
                dump_json(item.get('media_files', [])),
            ),
        )

    all_comments = load_json_file(comments_file, {})
    for news_id, comments in all_comments.items():
        conn.execute(
            'INSERT OR REPLACE INTO comments (news_id, comments_json) VALUES (?, ?)',
            (news_id, dump_json(comments)),
        )

    ads = load_json_file(ads_file, [])
    for ad in ads:
        if ad.get('text') and ad.get('link'):
            conn.execute('INSERT INTO ads (text, link) VALUES (?, ?)', (ad['text'], ad['link']))

    discuss_posts = load_json_file(discuss_file, [])
    for post in discuss_posts:
        if post.get('author') and post.get('title') and post.get('content'):
            conn.execute(
                'INSERT INTO discuss (author, title, content, date) VALUES (?, ?, ?, ?)',
                (post['author'], post['title'], post['content'], post.get('date')),
            )

    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='迁移旧 JSON 数据到 SQLite')
    parser.add_argument('--data', default='data.json')
    parser.add_argument('--comments', default='comments.json')
    parser.add_argument('--ads', default='ads.json')
    parser.add_argument('--discuss', default='discuss.json')
    parser.add_argument('--clear', action='store_true', help='迁移前清空 SQLite 现有数据')
    args = parser.parse_args()

    migrate(args.data, args.comments, args.ads, args.discuss, args.clear)
    print('迁移完成')


if __name__ == '__main__':
    main()
