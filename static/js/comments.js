(function() {
    let comments = [];
    let nextId = 1;
    let newsFileName = '';

    function initComments(filename) {
        newsFileName = filename;
        document.addEventListener('DOMContentLoaded', function() {
            loadComments();
            bindEvents();
        });
    }

    function bindEvents() {
        document.getElementById('submit-comment').addEventListener('click', function() {
            const text = document.getElementById('comment-content').value.trim();
            if (text) {
                addComment(text);
                document.getElementById('comment-content').value = '';
            }
        });
    }

    function addComment(content, parentId = null) {
        const comment = {
            id: nextId++,
            parentId: parentId,
            author: "匿名用户",
            date: new Date().toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }),
            content: content
        };
        comments.push(comment);
        saveComments();
        renderComments();
    }

    function saveComments() {
        fetch('/api/comments/' + newsFileName, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(comments)
        });
    }

    function renderComments() {
        const commentsList = document.getElementById('comments-list');
        commentsList.innerHTML = '';
        const topLevelComments = comments.filter(comment => !comment.parentId);
        topLevelComments.forEach(comment => {
            const commentElement = createCommentElement(comment);
            commentsList.appendChild(commentElement);
            const replies = comments.filter(c => c.parentId === comment.id);
            if (replies.length > 0) {
                const repliesContainer = document.createElement('div');
                repliesContainer.className = 'replies';
                replies.forEach(reply => repliesContainer.appendChild(createCommentElement(reply, true)));
                commentElement.appendChild(repliesContainer);
            }
        });
    }

    function createCommentElement(comment, isReply = false) {
        const li = document.createElement('li');
        li.className = isReply ? 'reply' : 'comment';
        li.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${comment.author}</span>
                <span class="comment-date">${comment.date}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            ${!isReply ? `<button class="reply-button" data-id="${comment.id}">回复</button>
            <div class="reply-form" id="reply-form-${comment.id}">
                <textarea placeholder="输入回复内容..."></textarea>
                <button class="submit-reply" data-parent="${comment.id}">发表回复</button>
            </div>` : ''}
        `;
        if (!isReply) {
            li.querySelector('.reply-button').addEventListener('click', function() {
                const form = document.getElementById(`reply-form-${comment.id}`);
                form.style.display = form.style.display === 'none' ? 'block' : 'none';
            });
            li.querySelector('.submit-reply').addEventListener('click', function() {
                const parentId = parseInt(this.getAttribute('data-parent'));
                const textarea = this.previousElementSibling;
                const content = textarea.value.trim();
                if (content) {
                    addComment(content, parentId);
                    textarea.value = '';
                    document.getElementById(`reply-form-${comment.id}`).style.display = 'none';
                }
            });
        }
        return li;
    }

    function loadComments() {
        fetch('/api/comments/' + newsFileName)
            .then(response => response.json())
            .then(data => {
                comments = data.comments || [];
                if (comments.length > 0) {
                    nextId = Math.max(...comments.map(c => c.id)) + 1;
                }
                renderComments();
            });
    }

    // 暴露初始化函数到全局作用域
    window.initComments = initComments;
})();