from flask import Blueprint, jsonify, request
from auth_utils import require_admin
from db import get_db_connection
import os
from config import UPLOAD_FOLDER
from logger import get_logger

# 创建日志记录器
logger = get_logger('admin')

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/api/admin/clear-all', methods=['POST'])
@require_admin
def clear_all_data():
    try:
        logger.warning(f'Admin clear all data request from {request.remote_addr}')
        conn = get_db_connection()
        
        # 清空所有表
        conn.execute('DELETE FROM news')
        conn.execute('DELETE FROM comments')
        conn.execute('DELETE FROM ads')
        conn.execute('DELETE FROM discuss')
        conn.execute('DELETE FROM users')
        conn.execute('DELETE FROM admin')
        conn.execute('DELETE FROM likes')
        
        conn.commit()
        conn.close()
        
        # 保留media_开头的文件，删除其他文件
        deleted_files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if not filename.startswith('media_'):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_files.append(filename)
        
        logger.info(f'Admin cleared all data successfully from {request.remote_addr}. Deleted files: {len(deleted_files)}')
        return jsonify({'message': '所有数据已清空'})
    except Exception as e:
        logger.error(f'Admin clear all data failed: {str(e)} from {request.remote_addr}')
        return jsonify({'error': f'清空失败: {str(e)}'}), 500