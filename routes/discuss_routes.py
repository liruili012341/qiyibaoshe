from flask import Blueprint, jsonify, request, session
from db import get_db_connection
import datetime

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
        # 检查用户是否登录
        if 'username' not in session:
            return jsonify({'error': '请先登录'}), 401

        post_data = request.get_json()
        title = post_data.get('title')
        content = post_data.get('content')

        if not title or not content:
            return jsonify({'error': '标题和内容不能为空'}), 400

        # 对标题和内容进行 XSS 防护
        import html
        title = html.escape(title)
        content = html.escape(content)

        # 使用登录用户的用户名和当前时间
        author = session['username']
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
