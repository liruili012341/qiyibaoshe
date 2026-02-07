from functools import wraps
from flask import jsonify, session


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            return jsonify({'error': '未授权访问'}), 401
        return f(*args, **kwargs)

    return decorated_function
