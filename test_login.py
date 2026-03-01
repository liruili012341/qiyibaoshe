import requests
import json

# 测试登录功能
response = requests.post(
    'http://localhost:8000/api/login',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'username': 'admin', 'password': 'admin123'})
)

print('Login response:', response.status_code)
print('Response content:', response.json())

# 测试登录状态检查
response = requests.get('http://localhost:8000/api/check-login')
print('\nCheck login response:', response.status_code)
print('Response content:', response.json())

# 测试注册功能
response = requests.post(
    'http://localhost:8000/api/register',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'username': 'testuser', 'password': 'testpassword'})
)

print('\nRegister response:', response.status_code)
print('Response content:', response.json())