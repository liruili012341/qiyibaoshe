import datetime
import os
import random
import string
from flask import Blueprint, jsonify, request, session, render_template

from auth_utils import require_admin
from config import UPLOAD_FOLDER
from db import dump_json, get_db_connection, load_json
from services.file_service import handle_file_upload
from services.news_service import save_news_to_db

news_bp = Blueprint('news', __name__)


def resolve_news_file(name):
    direct_path = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(direct_path):
        return direct_path

    base, _ext = os.path.splitext(name)
    candidates = []
    if base:
        for ext in ('.html', '.htm', '.txt'):
            candidates.append(os.path.join(UPLOAD_FOLDER, base + ext))

        for file_name in os.listdir(UPLOAD_FOLDER):
            if file_name.startswith(base + '.'):
                candidates.append(os.path.join(UPLOAD_FOLDER, file_name))

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


@news_bp.route('/api/news', methods=['POST'])
@require_admin
def upload_news():
    """新闻上传控制器"""
    title = request.form.get('title')
    content = request.form.get('content')

    # 验证输入
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400

    # 对标题和内容进行 XSS 防护
    import html
    title = html.escape(title)
    content = html.escape(content)

    # 处理文件上传
    files_info = []
    if 'files' in request.files:
        files = request.files.getlist('files')
        files_info = handle_file_upload(files)

    # 生成文件名和路径
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'news_{timestamp}.html'
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 使用模板引擎生成HTML
    html_content = render_template(
        'news_detail.html',
        title=title,
        content=content,
        publish_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        filename=filename
    )

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 保存到数据库
    save_news_to_db(filename, title, timestamp, files_info)

    return jsonify({'message': '新闻发布成功', 'filename': filename})


@news_bp.route('/api/files')
def list_files():
    referer = request.headers.get('Referer', '')
    if 'admin' in referer and ('is_admin' not in session or not session['is_admin']):
        return jsonify({'error': '未授权访问'}), 401

    conn = get_db_connection()
    rows = conn.execute('SELECT id, title, date, timestamp, media_files FROM news ORDER BY timestamp DESC').fetchall()
    conn.close()

    news = []
    for row in rows:
        resolved_path = resolve_news_file(row['id'])
        news.append(
            {
                'id': row['id'],
                'title': row['title'],
                'date': row['date'],
                'timestamp': row['timestamp'],
                'media_files': load_json(row['media_files'], []),
                'exists': bool(resolved_path),
                'resolved_name': os.path.basename(resolved_path) if resolved_path else None,
            }
        )
    return jsonify({'news': news})


@news_bp.route('/api/files/<filename>', methods=['DELETE'])
@require_admin
def delete_file(filename):
    # 验证 filename 参数，防止 SQL 注入
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+\.html$', filename):
        return jsonify({'error': '无效的文件名'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404

    os.remove(filepath)
    conn = get_db_connection()
    conn.execute('DELETE FROM news WHERE id = ?', (filename,))
    conn.execute('DELETE FROM comments WHERE news_id = ?', (filename,))
    conn.commit()
    conn.close()
    return jsonify({'message': '文件删除成功'})


@news_bp.route('/api/media')
@require_admin
def list_media():
    media_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith('media_'):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                media_files.append({'name': filename, 'time': os.path.getmtime(file_path)})

    media_files.sort(key=lambda x: x['time'], reverse=True)
    return jsonify({'media': media_files})


@news_bp.route('/api/temp-media-names')
@require_admin
def get_temp_media_names():
    media_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith('media_'):
            media_files.append(filename)
    return jsonify({'names': media_files})


@news_bp.route('/api/news/cleanup', methods=['POST'])
@require_admin
def cleanup_invalid_news():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT id FROM news').fetchall()
        deleted_count = 0
        
        for row in rows:
            news_id = row['id']
            news_path = os.path.join(UPLOAD_FOLDER, news_id)
            if not os.path.exists(news_path):
                # 删除新闻记录
                conn.execute('DELETE FROM news WHERE id = ?', (news_id,))
                # 删除相关评论
                conn.execute('DELETE FROM comments WHERE news_id = ?', (news_id,))
                deleted_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': f'清理完成，共删除 {deleted_count} 条失效新闻'})
    except Exception as e:
        return jsonify({'error': f'清理失败: {str(e)}'}), 500
