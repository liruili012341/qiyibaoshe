import requests
import json

# 1. 测试获取新闻列表，找到一条存在的新闻
print('=== 获取新闻列表 ===')
files_response = requests.get('http://localhost:8000/api/files')
print('Files response:', files_response.status_code)
files_data = files_response.json()
print('Response content:', files_data)

# 找到一条存在的新闻
news_id = None
if files_data.get('news'):
    for news in files_data['news']:
        if news['exists']:
            news_id = news['id']
            print(f'\n找到存在的新闻: {news_id}')
            break

if news_id:
    # 2. 测试获取评论
    print('\n=== 测试获取评论 ===')
    comments_response = requests.get(f'http://localhost:8000/api/comments/{news_id}')
    print('Comments response:', comments_response.status_code)
    print('Response content:', comments_response.json())

    # 3. 测试添加评论
    print('\n=== 测试添加评论 ===')
    comment_data = [{
        'id': 1,
        'parentId': None,
        'username': '测试用户',
        'time': '2026-02-28 21:00',
        'content': '这是一条测试评论'
    }]

    save_comments_response = requests.post(
        f'http://localhost:8000/api/comments/{news_id}',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(comment_data)
    )

    print('Save comments response:', save_comments_response.status_code)
    print('Response content:', save_comments_response.json())

    # 4. 再次获取评论，确认添加成功
    print('\n=== 再次获取评论 ===')
    comments_response = requests.get(f'http://localhost:8000/api/comments/{news_id}')
    print('Comments response:', comments_response.status_code)
    print('Response content:', comments_response.json())
else:
    print('\n未找到存在的新闻，无法测试评论功能')