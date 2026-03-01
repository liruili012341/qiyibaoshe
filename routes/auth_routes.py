from flask import Blueprint, jsonify, request, session
from db import get_db_connection, ph
from argon2.exceptions import VerifyMismatchError
import datetime
import random
import string
from logger import get_logger

# 创建日志记录器
logger = get_logger('auth')

auth_bp = Blueprint('auth', __name__)


# 生成验证码
def generate_captcha():
    # 生成4位数字验证码
    captcha = ''.join(random.choices(string.digits, k=4))
    return captcha


# 检查登录尝试次数和锁定状态
def check_login_attempts(ip_address, username):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 查找登录尝试记录
    cur.execute(
        'SELECT attempts, locked_until FROM login_attempts WHERE ip_address = ? AND username = ?',
        (ip_address, username)
    )
    row = cur.fetchone()
    
    now = datetime.datetime.now()
    
    if row:
        attempts = row['attempts']
        locked_until = row['locked_until']
        
        # 检查是否被锁定
        if locked_until:
            locked_until_time = datetime.datetime.fromisoformat(locked_until)
            if now < locked_until_time:
                conn.close()
                return {'locked': True, 'remaining_time': (locked_until_time - now).total_seconds()}
        
        # 检查尝试次数
        if attempts >= 4:
            # 锁定10分钟
            locked_until = (now + datetime.timedelta(minutes=10)).isoformat()
            cur.execute(
                'UPDATE login_attempts SET locked_until = ? WHERE ip_address = ? AND username = ?',
                (locked_until, ip_address, username)
            )
            conn.commit()
            conn.close()
            return {'require_captcha': True}
    
    conn.close()
    return {'locked': False, 'require_captcha': False}


# 更新登录尝试次数
def update_login_attempts(ip_address, username, success):
    conn = get_db_connection()
    cur = conn.cursor()
    
    now = datetime.datetime.now().isoformat()
    
    if success:
        # 登录成功，重置尝试次数
        cur.execute(
            'DELETE FROM login_attempts WHERE ip_address = ? AND username = ?',
            (ip_address, username)
        )
    else:
        # 登录失败，增加尝试次数
        cur.execute(
            '''
            INSERT INTO login_attempts (ip_address, username, attempts, last_attempt)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(ip_address, username) DO UPDATE SET
            attempts = attempts + 1,
            last_attempt = ?
            ''',
            (ip_address, username, now, now)
        )
    
    conn.commit()
    conn.close()


@auth_bp.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username') or request.form.get('username')
        password = data.get('password') or request.form.get('password')

        if not username or not password:
            logger.warning(f'Registration attempt without username or password from {request.remote_addr}')
            return jsonify({'error': '请提供用户名和密码'}), 400

        logger.info(f'Registration attempt for username: {username} from {request.remote_addr}')

        # 检查用户名是否已存在
        conn = get_db_connection()
        cur = conn.cursor()
        # 对用户名进行加密后再查询
        hashed_username = ph.hash(username)
        cur.execute('SELECT id FROM users WHERE username = ?', (hashed_username,))
        if cur.fetchone():
            conn.close()
            logger.warning(f'Registration failed: username {username} already exists from {request.remote_addr}')
            return jsonify({'error': '用户名已存在'}), 400

        # 创建新用户
        hashed_password = ph.hash(password)
        created_at = datetime.datetime.now().isoformat()
        cur.execute(
            'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
            (hashed_username, hashed_password, created_at)
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()

        # 登录新用户
        session['user_id'] = user_id
        session['username'] = username
        session['is_admin'] = False
        session.permanent = True
        logger.info(f'Registration successful for username: {username} from {request.remote_addr}')
        return jsonify({'message': '注册成功', 'username': username})
    except Exception as e:
        logger.error(f'Registration error: {str(e)} from {request.remote_addr}')
        return jsonify({'error': f'注册错误: {str(e)}'}), 500


@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username') or request.form.get('username')
        password = data.get('password') or request.form.get('password')
        captcha = data.get('captcha') or request.form.get('captcha')

        if not username or not password:
            logger.warning(f'Login attempt without username or password from {request.remote_addr}')
            return jsonify({'error': '请提供用户名和密码'}), 400

        # 获取用户IP地址
        ip_address = request.remote_addr or '127.0.0.1'
        logger.info(f'Login attempt for username: {username} from {ip_address}')

        # 检查登录尝试次数和锁定状态
        attempt_status = check_login_attempts(ip_address, username)
        if attempt_status['locked']:
            logger.warning(f'Login attempt blocked: account locked for username {username} from {ip_address}')
            return jsonify({'error': f'账号已被锁定，请{int(attempt_status["remaining_time"]/60)}分钟后再试'}), 423
        if attempt_status['require_captcha'] and not captcha:
            logger.info(f'Login attempt requires captcha for username {username} from {ip_address}')
            return jsonify({'require_captcha': True, 'error': '请输入验证码'}), 400

        # 对用户名进行加密
        hashed_username = ph.hash(username)

        # 首先尝试管理员登录
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password FROM admin WHERE username = ?', (hashed_username,))
        row = cur.fetchone()

        success = False

        if row:
            try:
                # 使用Argon2id验证密码
                ph.verify(row['password'], password)
                # 如果密码需要重新哈希（比如算法参数更新），则更新哈希值
                if ph.check_needs_rehash(row['password']):
                    conn.execute('UPDATE admin SET password = ? WHERE username = ?', (ph.hash(password), hashed_username))
                    conn.commit()
                session['is_admin'] = True
                session['username'] = username
                session.permanent = True
                success = True
                conn.close()
                update_login_attempts(ip_address, username, True)
                logger.info(f'Admin login successful for username: {username} from {ip_address}')
                return jsonify({'message': '登录成功', 'username': username, 'is_admin': True})
            except VerifyMismatchError:
                pass

        # 尝试普通用户登录
        cur.execute('SELECT id, password FROM users WHERE username = ?', (hashed_username,))
        row = cur.fetchone()
        conn.close()

        if row:
            try:
                # 使用Argon2id验证密码
                ph.verify(row['password'], password)
                # 如果密码需要重新哈希（比如算法参数更新），则更新哈希值
                if ph.check_needs_rehash(row['password']):
                    conn = get_db_connection()
                    conn.execute('UPDATE users SET password = ? WHERE id = ?', (ph.hash(password), row['id']))
                    conn.commit()
                    conn.close()
                session['user_id'] = row['id']
                session['username'] = username
                session['is_admin'] = False
                session.permanent = True
                success = True
                update_login_attempts(ip_address, username, True)
                logger.info(f'User login successful for username: {username} from {ip_address}')
                return jsonify({'message': '登录成功', 'username': username, 'is_admin': False})
            except VerifyMismatchError:
                pass

        # 登录失败，更新尝试次数
        update_login_attempts(ip_address, username, False)
        logger.warning(f'Login failed for username: {username} from {ip_address}')

        # 再次检查尝试次数，看是否需要验证码
        new_attempt_status = check_login_attempts(ip_address, username)
        if new_attempt_status['require_captcha']:
            logger.info(f'Login attempt now requires captcha for username {username} from {ip_address}')
            return jsonify({'require_captcha': True, 'error': '用户名或密码错误，请输入验证码'}), 401

        return jsonify({'error': '用户名或密码错误'}), 401
    except Exception as e:
        # 捕获所有异常并返回错误信息
        logger.error(f'Login error: {str(e)} from {request.remote_addr}')
        return jsonify({'error': f'登录错误: {str(e)}'}), 500


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    username = session.get('username', 'Unknown')
    logger.info(f'Logout attempt for username: {username} from {request.remote_addr}')
    session.pop('is_admin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    logger.info(f'Logout successful for username: {username} from {request.remote_addr}')
    return jsonify({'message': '登出成功'})


@auth_bp.route('/api/check-login')
def check_login():
    if 'user_id' in session or ('is_admin' in session and session['is_admin']):
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'logged_in': False}), 401
