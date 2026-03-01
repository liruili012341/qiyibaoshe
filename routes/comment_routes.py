from flask import Blueprint, jsonify, request, session
from db import dump_json, get_db_connection, load_json
import datetime

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
        
        # 验证 filename 参数，防止 SQL 注入
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', filename):
            return jsonify({'error': '无效的文件名'}), 400
        
        # 检查是否有新评论需要添加
        if comments_data and isinstance(comments_data, list) and len(comments_data) > 0:
            # 检查最后一条评论是否是新提交的
            new_comment = comments_data[-1]
            if 'username' not in new_comment or not new_comment['username']:
                # 如果没有用户名，检查用户是否登录
                if 'username' in session:
                    # 为已登录用户添加用户名和时间
                    new_comment['username'] = session['username']
                    new_comment['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # 未登录用户必须提供用户名
                    return jsonify({'error': '请先登录或提供用户名'}), 400
            else:
                # 对用户名和评论内容进行 XSS 防护
                import html
                new_comment['username'] = html.escape(new_comment['username'])
                if 'content' in new_comment:
                    new_comment['content'] = html.escape(new_comment['content'])
        
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
