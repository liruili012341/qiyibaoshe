from flask import Blueprint, jsonify, request
from db import get_db_connection

discuss_bp = Blueprint('discuss', __name__)


@discuss_bp.route('/api/discuss', methods=['GET'])
def get_discuss_posts():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT author, title, content, date FROM discuss ORDER BY id DESC').fetchall()
        conn.close()
        posts = [
            {'author': row['author'], 'title': row['title'], 'content': row['content'], 'date': row['date']}
            for row in rows
        ]
        return jsonify({'posts': posts})
    except Exception:
        return jsonify({'error': '获取失败'}), 500


@discuss_bp.route('/api/discuss', methods=['POST'])
def add_discuss_post():
    try:
        post_data = request.get_json()
        author = post_data.get('author')
        title = post_data.get('title')
        content = post_data.get('content')
        date = post_data.get('date')

        if not author or not title or not content:
            return jsonify({'error': '昵称、标题和内容不能为空'}), 400

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO discuss (author, title, content, date) VALUES (?, ?, ?, ?)',
            (author, title, content, date),
        )
        conn.commit()
        conn.close()
        return jsonify({'message': '帖子发表成功'})
    except Exception as e:
        return jsonify({'error': f'发表帖子失败: {str(e)}'}), 500
