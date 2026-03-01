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

# 3. 测试获取新闻列表，找到存在的新闻
print('\n=== 获取新闻列表 ===')
files_response = session.get('http://localhost:8000/api/files')
print('Files response:', files_response.status_code)
files_data = files_response.json()
print('Response content:', files_data)

# 找到存在的新闻
news_ids = []
news_titles = []
if files_data.get('news'):
    for news in files_data['news']:
        if news['exists']:
            news_ids.append(news['id'])
            news_titles.append(news['title'])
            if len(news_ids) >= 2:  # 最多选择2个新闻进行测试
                break

if news_ids:
    print(f'\n选择的新闻ID: {news_ids}')
    print(f'选择的新闻标题: {news_titles}')
    
    # 4. 测试下载功能
    print('\n=== 测试下载功能 ===')
    download_data = {
        'files': news_ids,
        'titles': news_titles
    }

    download_response = session.post(
        'http://localhost:8000/api/download',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(download_data)
    )

    print('Download response:', download_response.status_code)
    if download_response.status_code == 200:
        print('下载成功，文件大小:', len(download_response.content), 'bytes')
        # 保存下载的文件
        with open('test_download.zip', 'wb') as f:
            f.write(download_response.content)
        print('文件已保存为 test_download.zip')
    else:
        print('Response content:', download_response.json())
else:
    print('\n未找到存在的新闻，无法测试下载功能')