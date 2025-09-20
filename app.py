# app.py
from flask import Flask, request, jsonify, send_from_directory, session
import os
import datetime
import json
import random
import string
import re

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
ADMIN_TICKET_KEY = "THIS_IS_A_VERY_SECRET_KEY_FOR_ADMIN_ACCESS_2024"

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
# 上传新闻（需要管理员权限）
@app.route('/api/news', methods=['POST'])
@require_admin
def upload_news():
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

    # 创建新闻文件 (HTML格式)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"news_{timestamp}.html"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

# ... existing code ...
# 生成HTML内容
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 七一报社</title>
    <link rel="stylesheet" href="/news_styles.css">
</head>
<body>
    <header>
        <h1>七一报社</h1>
    </header>
    
    <div class="container">
        <a href="/" class="back-link">← 返回首页</a>
        
        <div class="news-content">
            <h1 class="news-title">{title}</h1>
            <div class="news-meta">{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            <div class="news-body">
                {content}
            </div>
        </div>
        
        <!-- 评论区域 -->
        <div class="comments-section">
            <h2 class="comments-title">评论</h2>
            
            <!-- 评论表单 -->
            <div class="comment-form">
                <textarea id="comment-content" placeholder="输入您的评论..."></textarea>
                <button id="submit-comment">发表评论</button>
            </div>
            
            <!-- 评论列表 -->
            <ul class="comments-list" id="comments-list">
                <!-- 评论将通过JavaScript动态加载 -->
            </ul>
        </div>
    </div>
    
    <script>
        // 初始化评论数据
        let comments = [];
        let nextId = 1;
        const newsFileName = '{filename}';
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            loadComments();
        }});
        
        // 提交评论
        document.getElementById('submit-comment').addEventListener('click', function() {{
            const content = document.getElementById('comment-content').value.trim();
            if (content) {{
                addComment(content);
                document.getElementById('comment-content').value = '';
            }}
        }});
        
        // 添加评论
        function addComment(content, parentId = null) {{
            const comment = {{
                id: nextId++,
                parentId: parentId,
                author: "匿名用户",
                date: new Date().toLocaleString('zh-CN', {{ year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }}),
                content: content
            }};
            
            comments.push(comment);
            saveComments();
            renderComments();
        }}
        
        // 保存评论到服务器
        function saveComments() {{
            fetch('/api/comments/' + newsFileName, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(comments)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.error) {{
                    console.error('保存评论失败:', data.error);
                }}
            }})
            .catch(error => {{
                console.error('保存评论失败:', error);
            }});
        }}
        
        // 渲染评论
        function renderComments() {{
            const commentsList = document.getElementById('comments-list');
            commentsList.innerHTML = '';
            
            // 获取一级评论
            const topLevelComments = comments.filter(comment => !comment.parentId);
            
            topLevelComments.forEach(comment => {{
                const commentElement = createCommentElement(comment);
                commentsList.appendChild(commentElement);
                
                // 获取回复评论
                const replies = comments.filter(c => c.parentId === comment.id);
                if (replies.length > 0) {{
                    const repliesContainer = document.createElement('div');
                    repliesContainer.className = 'replies';
                    
                    replies.forEach(reply => {{
                        const replyElement = createCommentElement(reply, true);
                        repliesContainer.appendChild(replyElement);
                    }});
                    
                    commentElement.appendChild(repliesContainer);
                }}
            }});
        }}
        
        // 创建评论元素
        function createCommentElement(comment, isReply = false) {{
            const li = document.createElement('li');
            li.className = isReply ? 'reply' : 'comment';
            
            li.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${{comment.author}}</span>
                    <span class="comment-date">${{comment.date}}</span>
                </div>
                <div class="comment-content">
                    ${{comment.content}}
                </div>
                ${{!isReply ? `<button class="reply-button" data-id="${{comment.id}}">回复</button>
                <div class="reply-form" id="reply-form-${{comment.id}}">
                    <textarea placeholder="输入回复内容..."></textarea>
                    <button class="submit-reply" data-parent="${{comment.id}}">发表回复</button>
                </div>` : ''}}
            `;
            
            // 添加回复按钮事件
            if (!isReply) {{
                const replyButton = li.querySelector('.reply-button');
                replyButton.addEventListener('click', function() {{
                    const form = document.getElementById(`reply-form-${{comment.id}}`);
                    form.style.display = form.style.display === 'none' ? 'block' : 'none';
                }});
                
                // 回复提交事件
                const submitReplyButton = li.querySelector('.submit-reply');
                submitReplyButton.addEventListener('click', function() {{
                    const parentId = parseInt(this.getAttribute('data-parent'));
                    const textarea = this.previousElementSibling;
                    const content = textarea.value.trim();
                    if (content) {{
                        addComment(content, parentId);
                        textarea.value = '';
                        document.getElementById(`reply-form-${{comment.id}}`).style.display = 'none';
                    }}
                }});
            }}
            
            return li;
        }}
        
        // 加载评论
        function loadComments() {{
            fetch('/api/comments/' + newsFileName)
            .then(response => response.json())
            .then(data => {{
                if (data.comments) {{
                    comments = data.comments;  // 使用服务器返回的评论数据
                    // 更新nextId以避免ID冲突
                    if (comments.length > 0) {{
                        nextId = Math.max(...comments.map(c => c.id)) + 1;
                    }}
                    renderComments();
                }}
            }})
            .catch(error => {{
                console.error('加载评论失败:', error);
            }});
        }}
    </script>
</body>
</html>"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

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

# 提供新闻样式文件（公开访问）
@app.route('/news_styles.css')
def news_styles():
    return send_from_directory('.', 'news_styles.css')



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
@require_admin
def delete_file(filename):
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

# 获取媒体文件列表
@app.route('/api/media')
@require_admin
def list_media():
    media_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith('media_'):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                media_files.append({
                    'name': filename,
                    'time': file_time
                })
    
    # 按时间倒序排序
    media_files.sort(key=lambda x: x['time'], reverse=True)
    
    return jsonify({'media': media_files})

# 提供上传的文件（公开访问）
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 新闻详情页面（公开访问）
@app.route('/news/<filename>')
def news_detail(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content

# ... existing code ...

# 创建数据文件
DATA_FILE = 'data.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'news': []}, f)

# 创建评论数据文件
COMMENTS_FILE = 'comments.json'
if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

# 创建广告数据文件
ADS_FILE = 'ads.json'
if not os.path.exists(ADS_FILE):
    with open(ADS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# 创建论坛数据文件
DISCUSS_FILE = 'discuss.json'
if not os.path.exists(DISCUSS_FILE):
    with open(DISCUSS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
@app.route('/api/comments/<filename>', methods=['GET'])
def get_comments(filename):
    try:
        # 从评论文件中读取评论数据
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            all_comments = json.load(f)
        
        # 获取特定新闻的评论
        news_comments = all_comments.get(filename, [])
        return jsonify({'comments': news_comments})
    except Exception as e:
        return jsonify({'comments': []})

# 保存新闻评论
@app.route('/api/comments/<filename>', methods=['POST'])
def save_comments(filename):
    try:
        # 获取请求中的评论数据
        comments_data = request.get_json()
        
        # 读取现有的所有评论
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            all_comments = json.load(f)
        
        # 更新特定新闻的评论
        all_comments[filename] = comments_data
        
        # 写回文件
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_comments, f, ensure_ascii=False, indent=2)
        
        return jsonify({'message': '评论保存成功'})
    except Exception as e:
        return jsonify({'error': f'保存评论失败: {str(e)}'}), 500

# 广告管理API
@app.route('/api/ads', methods=['GET'])
def get_ads():
    try:
        with open(ADS_FILE, 'r', encoding='utf-8') as f:
            ads = json.load(f)
        return jsonify({'ads': ads})
    except Exception as e:
        return jsonify({'error': '获取失败'}), 500

@app.route('/api/ads', methods=['POST'])
@require_admin
def add_ad():
    try:
        # 获取请求中的广告数据
        ad_data = request.get_json()
        ad_text = ad_data.get('text')
        ad_link = ad_data.get('link')
        
        if not ad_text or not ad_link:
            return jsonify({'error': '文本和链接不能为空'}), 400
        
        # 读取现有的广告
        with open(ADS_FILE, 'r', encoding='utf-8') as f:
            ads = json.load(f)
        
        # 添加新广告
        ads.append({
            'text': ad_text,
            'link': ad_link
        })
        
        # 写回文件
        with open(ADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ads, f, ensure_ascii=False, indent=2)
        
        return jsonify({'message': '广告添加成功'})
    except Exception as e:
        return jsonify({'error': f'添加广告失败: {str(e)}'}), 500

@app.route('/api/ads/<int:index>', methods=['DELETE'])
@require_admin
def delete_ad(index):
    try:
        # 读取现有的广告
        with open(ADS_FILE, 'r', encoding='utf-8') as f:
            ads = json.load(f)
        
        # 检查索引是否有效
        if index < 0 or index >= len(ads):
            return jsonify({'error': '友链索引无效'}), 400
        
        # 删除广告
        ads.pop(index)
        
        # 写回文件
        with open(ADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ads, f, ensure_ascii=False, indent=2)
        
        return jsonify({'message': '广告删除成功'})
    except Exception as e:
        return jsonify({'error': f'删除广告失败: {str(e)}'}), 500

# 打包下载功能
@app.route('/api/download', methods=['POST'])
@require_admin
def download_files():
    try:
        import zipfile
        from io import BytesIO
        
        # 获取请求中的文件列表
        data = request.get_json()
        file_ids = data.get('files', [])
        file_titles = data.get('titles', [])
        
        if not file_ids:
            return jsonify({'error': '请选择要下载的文件'}), 400
        
        # 创建内存中的ZIP文件
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加选中的新闻文件及其媒体文件
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data_store = json.load(f)
            
            for i, file_id in enumerate(file_ids):
                # 添加新闻HTML文件
                news_file_path = os.path.join(UPLOAD_FOLDER, file_id)
                if os.path.exists(news_file_path):
                    zipf.write(news_file_path, file_id)
                
                # 查找对应的新闻项以获取媒体文件
                news_item = next((item for item in data_store['news'] if item['id'] == file_id), None)
                if news_item and 'media_files' in news_item:
                    # 添加相关的媒体文件
                    for media_file in news_item['media_files']:
                        media_file_path = os.path.join(UPLOAD_FOLDER, media_file)
                        if os.path.exists(media_file_path):
                            zipf.write(media_file_path, media_file)
        
        memory_file.seek(0)
        
        # 返回ZIP文件
        from flask import send_file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='新闻打包下载.zip'
        )
    except Exception as e:
        return jsonify({'error': f'打包下载失败: {str(e)}'}), 500

# 论坛API
@app.route('/api/discuss', methods=['GET'])
def get_discuss_posts():
    try:
        with open(DISCUSS_FILE, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        # 按时间倒序排列
        posts.reverse()
        return jsonify({'posts': posts})
    except Exception as e:
        return jsonify({'error': '获取失败'}), 500

@app.route('/api/discuss', methods=['POST'])
def add_discuss_post():
    try:
        # 获取请求中的帖子数据
        post_data = request.get_json()
        author = post_data.get('author')
        title = post_data.get('title')
        content = post_data.get('content')
        date = post_data.get('date')
        
        if not author or not title or not content:
            return jsonify({'error': '昵称、标题和内容不能为空'}), 400
        
        # 读取现有的帖子
        with open(DISCUSS_FILE, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        
        # 添加新帖子
        posts.append({
            'author': author,
            'title': title,
            'content': content,
            'date': date
        })
        
        # 写回文件
        with open(DISCUSS_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        return jsonify({'message': '帖子发表成功'})
    except Exception as e:
        return jsonify({'error': f'发表帖子失败: {str(e)}'}), 500

@app.route('/discuss')
def discuss():
    return send_from_directory('.', 'discuss.html')

@app.route('/history')
def history():
    return send_from_directory('.', 'history.html')

@app.route('/uploads/<filename>')
def uploaded_news(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)