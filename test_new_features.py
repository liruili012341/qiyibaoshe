import requests
import json
import hashlib

# 创建一个会话对象，用于保存cookie
session = requests.Session()

# 1. 测试登录功能（明文传输，后端使用Argon2id加密）
print('=== 测试登录功能 ===')
username = 'admin'
password = 'admin123'

print(f'Attempting to login with username: {username}, password: {password}')

login_response = session.post(
    'http://localhost:8000/api/login',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'username': username, 'password': password})
)

print('Login response status code:', login_response.status_code)
print('Login response headers:', dict(login_response.headers))

try:
    print('Login response content:', login_response.json())
except Exception as e:
    print('Error parsing JSON response:', str(e))
    print('Raw response content:', login_response.text)

# 2. 检查登录状态
print('\n=== 检查登录状态 ===')
check_login_response = session.get('http://localhost:8000/api/check-login')
print('Check login response:', check_login_response.status_code)
print('Response content:', check_login_response.json())

# 3. 测试失效新闻清理功能
print('\n=== 测试失效新闻清理功能 ===')
cleanup_response = session.post('http://localhost:8000/api/news/cleanup')
print('Cleanup response:', cleanup_response.status_code)
print('Response content:', cleanup_response.json())

# 4. 测试获取新闻列表
print('\n=== 测试获取新闻列表 ===')
files_response = session.get('http://localhost:8000/api/files')
print('Files response:', files_response.status_code)
print('Response content:', files_response.json())

# 5. 测试一键清空所有数据功能（默认跳过，谨慎执行）
print('\n=== 测试一键清空所有数据功能 ===')
# 为了安全起见，默认跳过清空数据的测试
# 如果需要测试此功能，请将下面的confirm设置为'y'
confirm = 'n'
if confirm.lower() == 'y':
    clear_response = session.post('http://localhost:8000/api/admin/clear-all')
    print('Clear all response:', clear_response.status_code)
    print('Response content:', clear_response.json())
    
    # 再次获取新闻列表，确认数据已清空
    print('\n=== 再次获取新闻列表，确认数据已清空 ===')
    files_response = session.get('http://localhost:8000/api/files')
    print('Files response:', files_response.status_code)
    print('Response content:', files_response.json())
else:
    print('跳过清空所有数据测试')

# 6. 测试登出
print('\n=== 测试登出 ===')
logout_response = session.post('http://localhost:8000/api/logout')
print('Logout response:', logout_response.status_code)
print('Response content:', logout_response.json())

# 7. 再次检查登录状态
print('\n=== 再次检查登录状态 ===')
check_login_response = session.get('http://localhost:8000/api/check-login')
print('Check login response:', check_login_response.status_code)
print('Response content:', check_login_response.json())