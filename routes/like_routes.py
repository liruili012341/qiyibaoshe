from flask import Blueprint, jsonify, request, session
from db import get_db_connection
import datetime

like_bp = Blueprint('like', __name__)


@like_bp.route('/api/like', methods=['POST'])
def like_news():
    try:
        # 检查用户是否登录
        if 'user_id' not in session and ('is_admin' not in session or not session['is_admin']):
            return jsonify({'error': '请先登录'}), 401

        data = request.get_json(silent=True) or {}
        news_id = data.get('news_id')

        if not news_id:
            return jsonify({'error': '请提供新闻ID'}), 400

        # 获取用户ID
        user_id = session.get('user_id')
        if not user_id and session.get('is_admin'):
            # 管理员也可以点赞
            # 这里简单处理，为管理员创建一个虚拟用户ID
            # 实际项目中应该为管理员在用户表中创建记录
            user_id = -1

        conn = get_db_connection()
        cur = conn.cursor()

        # 检查是否已经点赞
        cur.execute('SELECT id FROM likes WHERE user_id = ? AND news_id = ?', (user_id, news_id))
        if cur.fetchone():
            conn.close()
            return jsonify({'error': '已经点过赞了'}), 400

        # 添加点赞记录
        created_at = datetime.datetime.now().isoformat()
        cur.execute(
            'INSERT INTO likes (user_id, news_id, created_at) VALUES (?, ?, ?)',
            (user_id, news_id, created_at)
        )
        conn.commit()

        # 获取点赞数
        cur.execute('SELECT COUNT(*) FROM likes WHERE news_id = ?', (news_id,))
        like_count = cur.fetchone()[0]
        conn.close()

        return jsonify({'message': '点赞成功', 'like_count': like_count})
    except Exception as e:
        return jsonify({'error': f'点赞错误: {str(e)}'}), 500


@like_bp.route('/api/unlike', methods=['POST'])
def unlike_news():
    try:
        # 检查用户是否登录
        if 'user_id' not in session and ('is_admin' not in session or not session['is_admin']):
            return jsonify({'error': '请先登录'}), 401

        data = request.get_json(silent=True) or {}
        news_id = data.get('news_id')

        if not news_id:
            return jsonify({'error': '请提供新闻ID'}), 400

        # 获取用户ID
        user_id = session.get('user_id')
        if not user_id and session.get('is_admin'):
            user_id = -1

        conn = get_db_connection()
        cur = conn.cursor()

        # 删除点赞记录
        cur.execute('DELETE FROM likes WHERE user_id = ? AND news_id = ?', (user_id, news_id))
        if cur.rowcount == 0:
            conn.close()
            return jsonify({'error': '未找到点赞记录'}), 400

        conn.commit()

        # 获取点赞数
        cur.execute('SELECT COUNT(*) FROM likes WHERE news_id = ?', (news_id,))
        like_count = cur.fetchone()[0]
        conn.close()

        return jsonify({'message': '取消点赞成功', 'like_count': like_count})
    except Exception as e:
        return jsonify({'error': f'取消点赞错误: {str(e)}'}), 500


@like_bp.route('/api/like-count/<news_id>')
def get_like_count(news_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM likes WHERE news_id = ?', (news_id,))
        like_count = cur.fetchone()[0]
        conn.close()

        # 检查当前用户是否已点赞
        is_liked = False
        if 'user_id' in session:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id FROM likes WHERE user_id = ? AND news_id = ?', (session['user_id'], news_id))
            is_liked = cur.fetchone() is not None
            conn.close()
        elif session.get('is_admin'):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id FROM likes WHERE user_id = ? AND news_id = ?', (-1, news_id))
            is_liked = cur.fetchone() is not None
            conn.close()

        return jsonify({'like_count': like_count, 'is_liked': is_liked})
    except Exception as e:
        return jsonify({'error': f'获取点赞数错误: {str(e)}'}), 500