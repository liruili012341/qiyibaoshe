import datetime
import os
import random
import string
from flask import Blueprint, jsonify, request, session

from auth_utils import require_admin
from config import UPLOAD_FOLDER
from db import dump_json, get_db_connection, load_json

news_bp = Blueprint('news', __name__)


@news_bp.route('/api/news', methods=['POST'])
@require_admin
def upload_news():
    title = request.form.get('title')
    content = request.form.get('content')

    files_info = []
    if 'files' in request.files:
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename:
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                extension = os.path.splitext(file.filename)[1]
                new_filename = f"media_{timestamp}_{random_str}{extension}"
                filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                file.save(filepath)
                files_info.append(new_filename)

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'news_{timestamp}.html'
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    html_content = f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{title} - 七一报社</title>
    <link rel=\"stylesheet\" href=\"/news_styles.css\">
</head>
<body>
    <header><h1>七一报社</h1></header>
    <div class=\"container\">
        <a href=\"/\" class=\"back-link\">← 返回首页</a>
        <div class=\"news-content\">
            <h1 class=\"news-title\">{title}</h1>
            <div class=\"news-meta\">{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            <div class=\"news-body\">{content}</div>
        </div>
        <div class=\"comments-section\">
            <h2 class=\"comments-title\">评论</h2>
            <div class=\"comment-form\">
                <textarea id=\"comment-content\" placeholder=\"输入您的评论...\"></textarea>
                <button id=\"submit-comment\">发表评论</button>
            </div>
            <ul class=\"comments-list\" id=\"comments-list\"></ul>
        </div>
    </div>
    <script>
        let comments = [];
        let nextId = 1;
        const newsFileName = '{filename}';

        document.addEventListener('DOMContentLoaded', function() {{ loadComments(); }});

        document.getElementById('submit-comment').addEventListener('click', function() {{
            const text = document.getElementById('comment-content').value.trim();
            if (text) {{
                addComment(text);
                document.getElementById('comment-content').value = '';
            }}
        }});

        function addComment(content, parentId = null) {{
            const comment = {{
                id: nextId++, parentId: parentId, author: "匿名用户",
                date: new Date().toLocaleString('zh-CN', {{ year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }}),
                content: content
            }};
            comments.push(comment);
            saveComments();
            renderComments();
        }}

        function saveComments() {{
            fetch('/api/comments/' + newsFileName, {{
                method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(comments)
            }});
        }}

        function renderComments() {{
            const commentsList = document.getElementById('comments-list');
            commentsList.innerHTML = '';
            const topLevelComments = comments.filter(comment => !comment.parentId);
            topLevelComments.forEach(comment => {{
                const commentElement = createCommentElement(comment);
                commentsList.appendChild(commentElement);
                const replies = comments.filter(c => c.parentId === comment.id);
                if (replies.length > 0) {{
                    const repliesContainer = document.createElement('div');
                    repliesContainer.className = 'replies';
                    replies.forEach(reply => repliesContainer.appendChild(createCommentElement(reply, true)));
                    commentElement.appendChild(repliesContainer);
                }}
            }});
        }}

        function createCommentElement(comment, isReply = false) {{
            const li = document.createElement('li');
            li.className = isReply ? 'reply' : 'comment';
            li.innerHTML = `
                <div class=\"comment-header\">
                    <span class=\"comment-author\">${{comment.author}}</span>
                    <span class=\"comment-date\">${{comment.date}}</span>
                </div>
                <div class=\"comment-content\">${{comment.content}}</div>
                ${{!isReply ? `<button class=\"reply-button\" data-id=\"${{comment.id}}\">回复</button>
                <div class=\"reply-form\" id=\"reply-form-${{comment.id}}\">
                    <textarea placeholder=\"输入回复内容...\"></textarea>
                    <button class=\"submit-reply\" data-parent=\"${{comment.id}}\">发表回复</button>
                </div>` : ''}}
            `;
            if (!isReply) {{
                li.querySelector('.reply-button').addEventListener('click', function() {{
                    const form = document.getElementById(`reply-form-${{comment.id}}`);
                    form.style.display = form.style.display === 'none' ? 'block' : 'none';
                }});
                li.querySelector('.submit-reply').addEventListener('click', function() {{
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

        function loadComments() {{
            fetch('/api/comments/' + newsFileName)
                .then(response => response.json())
                .then(data => {{
                    comments = data.comments || [];
                    if (comments.length > 0) nextId = Math.max(...comments.map(c => c.id)) + 1;
                    renderComments();
                }});
        }}
    </script>
</body>
</html>"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO news (id, title, date, timestamp, media_files) VALUES (?, ?, ?, ?, ?)',
        (filename, title, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), timestamp, dump_json(files_info)),
    )
    conn.commit()
    conn.close()

    return jsonify({'message': '新闻发布成功', 'filename': filename})


@news_bp.route('/api/files')
def list_files():
    referer = request.headers.get('Referer', '')
    if 'admin' in referer and ('is_admin' not in session or not session['is_admin']):
        return jsonify({'error': '未授权访问'}), 401

    conn = get_db_connection()
    rows = conn.execute('SELECT id, title, date, timestamp, media_files FROM news ORDER BY timestamp DESC').fetchall()
    conn.close()

    news = [
        {
            'id': row['id'],
            'title': row['title'],
            'date': row['date'],
            'timestamp': row['timestamp'],
            'media_files': load_json(row['media_files'], []),
        }
        for row in rows
    ]
    return jsonify({'news': news})


@news_bp.route('/api/files/<filename>', methods=['DELETE'])
@require_admin
def delete_file(filename):
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
