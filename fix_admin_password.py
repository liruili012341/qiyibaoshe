import sqlite3
from argon2 import PasswordHasher
from config import DB_FILE

ph = PasswordHasher()

# 连接数据库
conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row

# 检查admin表
cur = conn.cursor()
cur.execute('SELECT * FROM admin')
rows = cur.fetchall()

print('当前admin表内容:')
for row in rows:
    print(f'ID: {row["id"]}, Username: {row["username"]}, Password: {row["password"]}')

# 检查是否需要更新密码哈希
if rows:
    print('\n检查密码哈希格式...')
    for row in rows:
        # 检查密码哈希是否是Argon2格式
        if not row['password'].startswith('$argon2id$'):
            print(f'发现非Argon2格式的密码哈希，正在更新...')
            # 使用默认密码admin123重新哈希
            new_password_hash = ph.hash('admin123')
            cur.execute('UPDATE admin SET password = ? WHERE id = ?', (new_password_hash, row['id']))
            print(f'已更新用户 {row["username"]} 的密码哈希')
        else:
            print(f'用户 {row["username"]} 的密码哈希已经是Argon2格式')

    conn.commit()
    print('\n密码哈希检查和更新完成')
else:
    print('\nadmin表为空，正在创建默认管理员账号...')
    # 创建默认管理员账号
    default_username = 'admin'
    default_password = 'admin123'
    hashed_password = ph.hash(default_password)
    cur.execute(
        'INSERT INTO admin (username, password) VALUES (?, ?)',
        (default_username, hashed_password)
    )
    conn.commit()
    print('已创建默认管理员账号: admin / admin123')

# 关闭数据库连接
conn.close()
print('\n操作完成')