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

    filepath = resolve_news_file(filename)
    if not filepath:
        return (
            '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
            '<title>News Not Found</title></head><body>'
            '<h1>News content not found</h1>'
            '<p>Please return to the homepage and try another item.</p>'
            '</body></html>',
            404,
        )

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk', errors='replace') as f:
            content = f.read()
    return content
