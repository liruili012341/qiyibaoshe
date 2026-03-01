import requests
import json
import datetime

# 创建一个会话对象，用于保存cookie
session = requests.Session()

# 1. 登录
print('=== 登录测试 ===')
login_response = session.post(
    'http://localhost:8000/api/login',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'username': 'admin', 'password': 'admin123'})
)
print('Login response:', login_response.status_code)
print('Response content:', login_response.json())

# 2. 测试获取讨论帖子列表
print('\n=== 测试获取讨论帖子列表 ===')
discuss_response = session.get('http://localhost:8000/api/discuss')
print('Discuss response:', discuss_response.status_code)
print('Response content:', discuss_response.json())

# 3. 测试添加讨论帖子
print('\n=== 测试添加讨论帖子 ===')
discuss_data = {
    'title': '测试讨论帖子',
    'content': '这是一条测试讨论内容'
}

add_discuss_response = session.post(
    'http://localhost:8000/api/discuss',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(discuss_data)
)

print('Add discuss response:', add_discuss_response.status_code)
print('Response content:', add_discuss_response.json())

# 4. 再次获取讨论帖子列表，确认添加成功
print('\n=== 再次获取讨论帖子列表 ===')
discuss_response = session.get('http://localhost:8000/api/discuss')
print('Discuss response:', discuss_response.status_code)
print('Response content:', discuss_response.json())