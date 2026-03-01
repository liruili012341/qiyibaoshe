# 七一报社新闻管理系统

一个基于 Flask 的轻量级新闻管理系统，支持新闻发布、多媒体内容管理、内容搜索、用户系统和点赞功能等。

## 功能特点

- 📰 **新闻发布**：支持富文本新闻内容发布
- 📎 **多媒体支持**：可为每篇新闻添加图片和视频附件
- 🔒 **用户系统**：支持用户注册、登录和登出
- 👍 **新闻点赞**：已登录用户可以对新闻进行点赞
- 🔐 **安全认证**：基于账号密码的认证机制，使用 Argon2id 加密
- 🛡️ **登录保护**：登录失败 5 次后要求输入验证码，防止暴力破解
- � **内容搜索**：支持新闻标题和内容的实时搜索
- 📂 **内容管理**：可视化后台管理界面，支持新闻删除
- 🗑️ **失效新闻清理**：一键清理文件不存在的失效新闻
- 🧹 **一键清空数据**：快速清空所有数据（谨慎使用），包括用户账号
- 📱 **响应式设计**：适配各种设备屏幕尺寸
- 📝 **内容折叠**：长内容自动折叠，提升阅读体验
- 💬 **评论系统**：支持用户评论，已登录用户自动带用户名和时间
- 🗣️ **论坛系统**：支持用户发帖，已登录用户自动带用户名和时间

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML5 + CSS3 + JavaScript (原生)
- **数据存储**：SQLite
- **会话管理**：Flask Session
- **密码加密**：Argon2id

## 快速开始

### 环境要求

- Python 3.6+
- pip 包管理器

### 安装步骤

1. 克隆项目代码：
https://github.com/liruili012341/qiyibaoshe/releases/download/%E4%B8%83%E4%B8%80%E6%8A%A5%E7%A4%BE2.9/qybs2.9.zip

2. 安装依赖：
```bash
pip install flask argon2-cffi
```

3. 启动服务：
```bash
python app.py

# 如需迁移旧 JSON 数据
python migrate_json_to_sqlite.py --clear
```

4. 访问应用：
   - 前台页面：http://localhost:8000
   - 管理后台：http://localhost:8000/admin

### 管理员登录

1. 访问管理后台：http://localhost:8000/admin
2. 输入默认管理员账号：admin / admin123
3. 登录后即可进入管理界面

### 用户注册

1. 访问前台页面：http://localhost:8000
2. 点击"注册"按钮
3. 填写用户名和密码
4. 注册成功后自动登录

## 使用说明

### 发布新闻

1. 登录管理后台
2. 点击"新闻发布"标签
3. 填写新闻标题和内容
4. 可选择上传图片或视频附件
5. 点击"发布新闻"

### 管理内容

1. 登录管理后台
2. 点击"内容管理"标签
3. 输入安全码并点击"加载内容列表"
4. 可查看所有新闻并进行删除操作

### 前台浏览

- 首页展示最新新闻列表
- 支持关键词搜索新闻
- 点击新闻标题查看详细内容
- 长内容支持折叠/展开功能
- 已登录用户可以对新闻进行点赞
- 已登录用户可以发表评论，自动带用户名和时间

### 论坛使用

1. 访问论坛页面：http://localhost:8000/discuss
2. 登录后可以发表帖子，自动带用户名和时间
3. 查看其他用户发表的帖子

## 安全说明

1. **密码加密**：使用 Argon2id 对用户名和密码进行加密存储
2. **登录保护**：登录失败 5 次后要求输入验证码，防止暴力破解
3. **XSS 防护**：对用户输入的内容进行 HTML 转义，防止跨站脚本攻击
4. **SQL 注入防护**：使用参数化查询，防止 SQL 注入攻击
5. **会话管理**：使用 Flask Session 管理用户登录状态
6. **生产部署**：在生产环境中，请修改 [app.py](file://d:\1\project\qybs\app.py) 中的 `secret_key` 为复杂随机字符串

## 目录结构

```
qybs/
├── app.py                      # 应用入口
├── config.py                   # 路径与配置
├── db.py                       # SQLite 连接与建表
├── routes/                     # 按功能拆分的路由
│   ├── __init__.py             # 路由初始化
│   ├── ad_routes.py            # 广告相关路由
│   ├── admin_routes.py         # 管理员相关路由
│   ├── auth_routes.py          # 认证相关路由（登录、注册）
│   ├── comment_routes.py       # 评论相关路由
│   ├── discuss_routes.py       # 论坛相关路由
│   ├── download_routes.py      # 下载相关路由
│   ├── like_routes.py          # 点赞相关路由
│   ├── news_routes.py          # 新闻相关路由
│   └── pages_routes.py         # 页面相关路由
├── services/                   # 业务逻辑服务
│   ├── __init__.py             # 服务初始化
│   ├── file_service.py         # 文件处理服务
│   └── news_service.py         # 新闻处理服务
├── static/                     # 静态资源
│   └── js/                     # JavaScript 文件
├── templates/                  # HTML 模板
│   ├── admin.html              # 管理后台页面
│   ├── discuss.html            # 论坛页面
│   ├── history.html            # 历史新闻页面
│   ├── index.html              # 首页
│   ├── login.html              # 登录页面
│   └── news_detail.html        # 新闻详情页模板
├── uploads/                    # 上传文件目录
├── auth_utils.py               # 认证工具
├── fix_admin_password.py       # 修复管理员密码工具
├── migrate_json_to_sqlite.py   # JSON -> SQLite 迁移脚本
├── news_styles.css             # 新闻样式文件
├── site.db                     # SQLite 数据库文件
├── test_ads.py                 # 广告测试脚本
├── test_comments.py            # 评论测试脚本
├── test_discuss.py             # 论坛测试脚本
├── test_download.py            # 下载测试脚本
├── test_login.py               # 登录测试脚本
├── test_new_features.py        # 新功能测试脚本
├── test_news.py                # 新闻测试脚本
└── README.md                   # 项目说明文件
```

## 文件说明

### 核心文件
- **app.py**：应用入口，初始化 Flask 应用，注册路由
- **config.py**：配置文件，定义路径和系统配置
- **db.py**：数据库操作，连接 SQLite 数据库，创建表结构

### 路由文件
- **routes/auth_routes.py**：处理用户注册、登录、登出等认证相关功能
- **routes/like_routes.py**：处理新闻点赞和取消点赞功能
- **routes/comment_routes.py**：处理新闻评论功能
- **routes/discuss_routes.py**：处理论坛发帖功能
- **routes/news_routes.py**：处理新闻发布、删除等功能
- **routes/admin_routes.py**：处理管理员相关功能，如清空数据

### 服务文件
- **services/file_service.py**：处理文件上传和管理
- **services/news_service.py**：处理新闻相关业务逻辑

### 模板文件
- **templates/index.html**：首页，展示新闻列表和搜索功能
- **templates/admin.html**：管理后台，用于发布和管理新闻
- **templates/discuss.html**：论坛页面，用于发帖和查看帖子
- **templates/news_detail.html**：新闻详情页模板

### 测试文件
- **test_login.py**：测试登录和注册功能
- **test_news.py**：测试新闻发布和管理功能
- **test_comments.py**：测试评论功能
- **test_discuss.py**：测试论坛发帖功能

## 配置说明

在 [config.py](file://d:\1\project\qybs\config.py) 中可以修改以下配置：

- **SECRET_KEY**：Flask 应用密钥（生产环境必须修改）
- **UPLOAD_FOLDER**：上传文件存储目录
- **WEB_FOLDER**：HTML 模板文件目录
- **NEWS_STYLE_FILE**：新闻样式文件路径
- **DB_FILE**：SQLite 数据库文件路径

## 部署建议

### 生产环境部署

1. 修改 [SECRET_KEY](file://d:\1\project\qybs\config.py) 为强随机字符串
2. 使用 Nginx 或 Apache 作为反向代理
3. 配置 SSL 证书启用 HTTPS
4. 使用 Gunicorn 或 uWSGI 作为应用服务器
5. 定期备份数据库文件
6. 配置防火墙，限制访问端口

