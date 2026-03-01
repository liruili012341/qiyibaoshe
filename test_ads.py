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

# 3. 测试获取广告列表
print('\n=== 测试获取广告列表 ===')
ads_response = session.get('http://localhost:8000/api/ads')
print('Ads response:', ads_response.status_code)
print('Response content:', ads_response.json())

# 4. 测试添加广告
print('\n=== 测试添加广告 ===')
ad_data = {
    'text': '测试广告',
    'link': 'http://example.com'
}

add_ad_response = session.post(
    'http://localhost:8000/api/ads',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(ad_data)
)

print('Add ad response:', add_ad_response.status_code)
print('Response content:', add_ad_response.json())

# 5. 再次获取广告列表，确认添加成功
print('\n=== 再次获取广告列表 ===')
ads_response = session.get('http://localhost:8000/api/ads')
print('Ads response:', ads_response.status_code)
ads_data = ads_response.json()
print('Response content:', ads_data)

# 6. 测试删除广告（删除刚添加的测试广告）
if ads_data.get('ads'):
    # 获取刚添加的测试广告ID
    test_ad = None
    for ad in ads_data['ads']:
        if ad['text'] == '测试广告':
            test_ad = ad
            break
    
    if test_ad:
        print('\n=== 测试删除广告 ===')
        delete_response = session.delete(f'http://localhost:8000/api/ads/{test_ad["id"]}')
        print('Delete response:', delete_response.status_code)
        print('Response content:', delete_response.json())
        
        # 再次获取广告列表，确认删除成功
        print('\n=== 再次获取广告列表 ===')
        ads_response = session.get('http://localhost:8000/api/ads')
        print('Ads response:', ads_response.status_code)
        print('Response content:', ads_response.json())
    else:
        print('\n未找到测试广告')