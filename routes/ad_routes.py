from flask import Blueprint, jsonify, request
from auth_utils import require_admin
from db import get_db_connection

ads_bp = Blueprint('ads', __name__)


@ads_bp.route('/api/ads', methods=['GET'])
def get_ads():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT id, text, link FROM ads ORDER BY id ASC').fetchall()
        conn.close()
        ads = [{'id': row['id'], 'text': row['text'], 'link': row['link']} for row in rows]
        return jsonify({'ads': ads})
    except Exception:
        return jsonify({'error': '获取失败'}), 500


@ads_bp.route('/api/ads', methods=['POST'])
@require_admin
def add_ad():
    try:
        ad_data = request.get_json()
        ad_text = ad_data.get('text')
        ad_link = ad_data.get('link')

        if not ad_text or not ad_link:
            return jsonify({'error': '文本和链接不能为空'}), 400

        conn = get_db_connection()
        conn.execute('INSERT INTO ads (text, link) VALUES (?, ?)', (ad_text, ad_link))
        conn.commit()
        conn.close()
        return jsonify({'message': '广告添加成功'})
    except Exception as e:
        return jsonify({'error': f'添加广告失败: {str(e)}'}), 500


@ads_bp.route('/api/ads/<int:ad_id>', methods=['DELETE'])
@require_admin
def delete_ad(ad_id):
    try:
        conn = get_db_connection()
        result = conn.execute('DELETE FROM ads WHERE id = ?', (ad_id,))
        conn.commit()
        conn.close()

        if result.rowcount == 0:
            return jsonify({'error': '友链索引无效'}), 400
        return jsonify({'message': '广告删除成功'})
    except Exception as e:
        return jsonify({'error': f'删除广告失败: {str(e)}'}), 500
