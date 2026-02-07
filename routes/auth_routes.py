from flask import Blueprint, jsonify, request, session
from config import ADMIN_TICKET_KEY

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    if 'ticket' not in request.files:
        return jsonify({'error': '请上传门票文件'}), 400

    ticket_file = request.files['ticket']
    if ticket_file.filename == '':
        return jsonify({'error': '请选择门票文件'}), 400

    try:
        ticket_content = ticket_file.read().decode('utf-8').strip()
        if ticket_content == ADMIN_TICKET_KEY:
            session['is_admin'] = True
            session.permanent = True
            return jsonify({'message': '登录成功'})
        return jsonify({'error': '门票验证失败'}), 401
    except Exception:
        return jsonify({'error': '门票文件读取失败'}), 400


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return jsonify({'message': '已登出'})


@auth_bp.route('/api/check-login')
def check_login():
    if 'is_admin' in session and session['is_admin']:
        return jsonify({'logged_in': True})
    return jsonify({'logged_in': False}), 401
