# app.py
from flask import Flask, request, jsonify, send_from_directory, session
import os
import datetime
import json
import random
import string

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-here-change-in-production'  # 请在生产环境中更改

# 创建上传目录
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 创建数据文件
DATA_FILE = 'data.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'news': []}, f)

# 管理员门票密钥（应保存在安全的地方，比如环境变量中）
ADMIN_TICKET_KEY = "THIS_IS_A_VERY_SECRET_KEY_FOR_ADMIN_ACCESS_2023"

# 首页
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 管理页面
@app.route('/admin')
def admin():
    # 检查是否已登录
    if 'is_admin' not in session or not session['is_admin']:
        return send_from_directory('.', 'login.html')
    return send_from_directory('.', 'admin.html')

# 登录页面
@app.route('/login')
def login_page():
    # 如果已经登录，直接跳转到管理页面
    if 'is_admin' in session and session['is_admin']:
        return send_from_directory('.', 'admin.html')
    return send_from_directory('.', 'login.html')

# 门票验证接口
@app.route('/api/login', methods=['POST'])
def login():
    if 'ticket' not in request.files:
        return jsonify({'error': '请上传门票文件'}), 400
    
    ticket_file = request.files['ticket']
    if ticket_file.filename == '':
        return jsonify({'error': '请选择门票文件'}), 400
    
    try:
        # 读取门票文件内容
        ticket_content = ticket_file.read().decode('utf-8').strip()
        
        # 验证门票
        if ticket_content == ADMIN_TICKET_KEY:
            # 登录成功，设置session
            session['is_admin'] = True
            session.permanent = True  # 设置为永久session
            return jsonify({'message': '登录成功'})
        else:
            return jsonify({'error': '门票验证失败'}), 401
    except Exception as e:
        return jsonify({'error': '门票文件读取失败'}), 400

# 登出接口
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return jsonify({'message': '已登出'})

# 检查登录状态
@app.route('/api/check-login')
def check_login():
    if 'is_admin' in session and session['is_admin']:
        return jsonify({'logged_in': True})
    else:
        return jsonify({'logged_in': False}), 401

# 需要管理员权限的装饰器
def require_admin(f):
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            return jsonify({'error': '未授权访问'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 上传新闻（需要管理员权限）
@app.route('/api/news', methods=['POST'])
def upload_news():
    # 检查登录状态
    if 'is_admin' not in session or not session['is_admin']:
        return jsonify({'error': '未授权访问'}), 401
        
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        title = request.form.get('title')
        content = request.form.get('content')

        # 处理文件上传
        files_info = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    extension = os.path.splitext(file.filename)[1]
                    new_filename = f"media_{timestamp}_{random_str}{extension}"
                    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                    file.save(filepath)
                    files_info.append(new_filename)

        # 创建新闻文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"news_{timestamp}.txt"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(content or "")
            f.write("\n---MEDIA_FILES---\n")
            for media_file in files_info:
                f.write(f"{media_file}\n")

        # 更新数据文件
        with open(DATA_FILE, 'r+', encoding='utf-8') as f:
            data_store = json.load(f)
            news_item = {
                'id': filename,
                'title': title,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                'timestamp': timestamp,
                'media_files': files_info
            }
            data_store['news'].append(news_item)
            f.seek(0)
            json.dump(data_store, f, ensure_ascii=False, indent=2)
            f.truncate()

        return jsonify({'message': '新闻发布成功', 'filename': filename})

    else:
        # JSON 提交（旧逻辑）
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"news_{timestamp}.txt"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(content or "")

        with open(DATA_FILE, 'r+', encoding='utf-8') as f:
            data_store = json.load(f)
            data_store['news'].append({
                'id': filename,
                'title': title,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                'timestamp': timestamp
            })
            f.seek(0)
            json.dump(data_store, f, ensure_ascii=False, indent=2)
            f.truncate()

        return jsonify({'message': '新闻发布成功', 'filename': filename})

# 获取文件列表（首页公开访问，管理页面需要权限）
@app.route('/api/files')
def list_files():
    # 检查是否来自管理页面的请求
    referer = request.headers.get('Referer', '')
    if 'admin' in referer:
        # 管理页面的请求需要验证权限
        if 'is_admin' not in session or not session['is_admin']:
            return jsonify({'error': '未授权访问'}), 401

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data_store = json.load(f)

    data_store['news'].sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(data_store)

# 删除文件（需要管理员权限）
@app.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    # 检查登录状态
    if 'is_admin' not in session or not session['is_admin']:
        return jsonify({'error': '未授权访问'}), 401

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        with open(DATA_FILE, 'r+', encoding='utf-8') as f:
            data_store = json.load(f)
            data_store['news'] = [item for item in data_store['news'] if item['id'] != filename]
            f.seek(0)
            json.dump(data_store, f, ensure_ascii=False, indent=2)
            f.truncate()
        return jsonify({'message': '文件删除成功'})
    else:
        return jsonify({'error': '文件不存在'}), 404

# 获取新闻内容（公开访问）
@app.route('/api/news/<filename>')
def get_news(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) < 2:
        return jsonify({'error': '文件格式错误'}), 400

    title = lines[0].strip()
    date = lines[1].strip()

    media_separator_index = -1
    content_lines = []
    media_files = []

    for i, line in enumerate(lines[2:], 2):
        if line.strip() == '---MEDIA_FILES---':
            media_separator_index = i
            break
        content_lines.append(line)

    content = ''.join(content_lines)

    if media_separator_index != -1 and media_separator_index + 1 < len(lines):
        media_files = [line.strip() for line in lines[media_separator_index + 1:] if line.strip()]

    return jsonify({
        'title': title,
        'date': date,
        'content': content,
        'media_files': media_files
    })

# 提供上传的文件（公开访问）
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 新闻详情页面（公开访问）
@app.route('/news/<filename>')
def news_detail(filename):
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新闻详情 - 七一报社</title>
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f0f8ff;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            header {{
                background-color: #1e90ff;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .news-title {{
                font-size: 28px;
                margin-bottom: 10px;
            }}
            .news-meta {{
                color: #e6f2ff;
                font-size: 16px;
                margin-bottom: 20px;
            }}
            .news-content {{
                background-color: white;
                padding: 30px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .media-content {{
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .media-item {{
                margin-bottom: 20px;
                text-align: center;
            }}
            .media-item img {{
                max-width: 100%;
                height: auto;
                border-radius: 5px;
            }}
            .media-item video {{
                max-width: 100%;
                height: auto;
                border-radius: 5px;
            }}
            .back-link {{
                display: inline-block;
                margin-bottom: 20px;
                color: #1e90ff;
                text-decoration: none;
            }}
            .back-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>七一报社</h1>
        </header>
        
        <div class="container">
            <a href="/" class="back-link">← 返回首页</a>
            
            <div class="news-content">
                <h1 class="news-title" id="news-title">加载中...</h1>
                <div class="news-meta" id="news-date">加载中...</div>
                <div id="news-content">加载中...</div>
            </div>
            
            <div id="media-content" style="display:none;">
                <h2>媒体内容</h2>
                <div id="media-list"></div>
            </div>
        </div>

        <script>
            // 获取新闻详情
            fetch('/api/news/{filename}')
            .then(response => response.json())
            .then(data => {{
                if (data.error) {{
                    document.getElementById('news-title').textContent = '加载失败';
                    document.getElementById('news-content').textContent = data.error;
                }} else {{
                    document.getElementById('news-title').textContent = data.title;
                    document.getElementById('news-date').textContent = data.date;
                    document.getElementById('news-content').innerHTML = data.content.replace(/\\n/g, '<br>');
                    
                    // 处理媒体文件
                    if (data.media_files && data.media_files.length > 0) {{
                        document.getElementById('media-content').style.display = 'block';
                        let mediaHTML = '';
                        data.media_files.forEach(mediaFile => {{
                            const fileExtension = mediaFile.split('.').pop().toLowerCase();
                            if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExtension)) {{
                                // 图片文件
                                mediaHTML += `
                                    <div class="media-item">
                                        <img src="/uploads/${{mediaFile}}" alt="新闻图片">
                                    </div>
                                `;
                            }} else if (['mp4', 'webm', 'ogg', 'avi', 'mov'].includes(fileExtension)) {{
                                // 视频文件
                                mediaHTML += `
                                    <div class="media-item">
                                        <video controls>
                                            <source src="/uploads/${{mediaFile}}" type="video/${{fileExtension}}">
                                            您的浏览器不支持视频播放。
                                        </video>
                                    </div>
                                `;
                            }}
                        }});
                        document.getElementById('media-list').innerHTML = mediaHTML;
                    }}
                }}
            }})
            .catch(error => {{
                document.getElementById('news-title').textContent = '加载失败';
                document.getElementById('news-content').textContent = error.message;
            }});
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)