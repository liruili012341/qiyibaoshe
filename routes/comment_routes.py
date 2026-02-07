from flask import Blueprint, jsonify, request
from db import dump_json, get_db_connection, load_json

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/api/comments/<filename>', methods=['GET'])
def get_comments(filename):
    try:
        conn = get_db_connection()
        row = conn.execute('SELECT comments_json FROM comments WHERE news_id = ?', (filename,)).fetchone()
        conn.close()
        news_comments = load_json(row['comments_json'], []) if row else []
        return jsonify({'comments': news_comments})
    except Exception:
        return jsonify({'comments': []})


@comments_bp.route('/api/comments/<filename>', methods=['POST'])
def save_comments(filename):
    try:
        comments_data = request.get_json()
        conn = get_db_connection()
        conn.execute(
            '''
            INSERT INTO comments (news_id, comments_json)
            VALUES (?, ?)
            ON CONFLICT(news_id) DO UPDATE SET comments_json = excluded.comments_json
            ''',
            (filename, dump_json(comments_data or [])),
        )
        conn.commit()
        conn.close()
        return jsonify({'message': '评论保存成功'})
    except Exception as e:
        return jsonify({'error': f'保存评论失败: {str(e)}'}), 500
