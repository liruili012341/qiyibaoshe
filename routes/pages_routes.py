import os
from flask import Blueprint, jsonify, send_file, send_from_directory, session
from config import NEWS_STYLE_FILE, UPLOAD_FOLDER, WEB_FOLDER

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    return send_from_directory(WEB_FOLDER, 'index.html')


@pages_bp.route('/admin')
def admin():
    if 'is_admin' not in session or not session['is_admin']:
        return send_from_directory(WEB_FOLDER, 'login.html')
    return send_from_directory(WEB_FOLDER, 'admin.html')


@pages_bp.route('/login')
def login_page():
    if 'is_admin' in session and session['is_admin']:
        return send_from_directory(WEB_FOLDER, 'admin.html')
    return send_from_directory(WEB_FOLDER, 'login.html')


@pages_bp.route('/discuss')
def discuss_page():
    return send_from_directory(WEB_FOLDER, 'discuss.html')


@pages_bp.route('/history')
def history_page():
    return send_from_directory(WEB_FOLDER, 'history.html')


@pages_bp.route('/news_styles.css')
def news_styles():
    return send_file(NEWS_STYLE_FILE)


@pages_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@pages_bp.route('/news/<filename>')
def news_detail(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return content
