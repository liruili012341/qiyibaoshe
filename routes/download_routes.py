import os
import zipfile
from io import BytesIO

from flask import Blueprint, jsonify, request, send_file

from auth_utils import require_admin
from config import UPLOAD_FOLDER
from db import get_db_connection, load_json

download_bp = Blueprint('download', __name__)


@download_bp.route('/api/download', methods=['POST'])
@require_admin
def download_files():
    try:
        data = request.get_json()
        file_ids = data.get('files', [])

        if not file_ids:
            return jsonify({'error': '请选择要下载的文件'}), 400

        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            conn = get_db_connection()
            for file_id in file_ids:
                news_file_path = os.path.join(UPLOAD_FOLDER, file_id)
                if os.path.exists(news_file_path):
                    zipf.write(news_file_path, file_id)

                row = conn.execute('SELECT media_files FROM news WHERE id = ?', (file_id,)).fetchone()
                if row:
                    for media_file in load_json(row['media_files'], []):
                        media_file_path = os.path.join(UPLOAD_FOLDER, media_file)
                        if os.path.exists(media_file_path):
                            zipf.write(media_file_path, media_file)
            conn.close()

        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='新闻打包下载.zip',
        )
    except Exception as e:
        return jsonify({'error': f'打包下载失败: {str(e)}'}), 500
