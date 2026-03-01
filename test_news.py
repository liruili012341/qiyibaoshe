import requests
import json

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

# 2. 检查登录状态
print('\n=== 检查登录状态 ===')
check_login_response = session.get('http://localhost:8000/api/check-login')
print('Check login response:', check_login_response.status_code)
print('Response content:', check_login_response.json())

# 3. 测试新闻发布
print('\n=== 测试新闻发布 ===')
news_data = {
    'title': '测试新闻',
    'content': '<p>这是一条测试新闻内容</p>'
}

# 直接发送表单数据
news_response = session.post(
    'http://localhost:8000/api/news',
    data=news_data
)

print('News publish response:', news_response.status_code)
print('Response content:', news_response.json())

# 4. 测试获取新闻列表
print('\n=== 测试获取新闻列表 ===')
files_response = session.get('http://localhost:8000/api/files')
print('Files response:', files_response.status_code)
files_data = files_response.json()
print('Response content:', files_data)

# 5. 测试删除新闻（删除刚发布的测试新闻）
if files_data.get('news'):
    # 获取刚发布的测试新闻ID
    test_news = None
    for news in files_data['news']:
        if news['title'] == '测试新闻':
            test_news = news
            break
    
    if test_news:
        print('\n=== 测试删除新闻 ===')
        delete_response = session.delete(f'http://localhost:8000/api/files/{test_news["id"]}')
        print('Delete response:', delete_response.status_code)
        print('Response content:', delete_response.json())
        
        # 再次获取新闻列表，确认删除成功
        print('\n=== 再次获取新闻列表 ===')
        files_response = session.get('http://localhost:8000/api/files')
        print('Files response:', files_response.status_code)
        print('Response content:', files_response.json())
    else:
        print('\n未找到测试新闻')