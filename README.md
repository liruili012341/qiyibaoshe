# 七一报社新闻管理系统

一个基于 Flask 的轻量级新闻管理系统，支持新闻发布、多媒体内容管理、内容搜索和折叠展示等功能。

## 功能特点

- 📰 **新闻发布**：支持富文本新闻内容发布
- 📎 **多媒体支持**：可为每篇新闻添加图片和视频附件
- 🔒 **门票认证**：基于文件的管理员认证机制，安全便捷
- 🔍 **内容搜索**：支持新闻标题和内容的实时搜索
- 📂 **内容管理**：可视化后台管理界面，支持新闻删除
- 📱 **响应式设计**：适配各种设备屏幕尺寸
- 📝 **内容折叠**：长内容自动折叠，提升阅读体验

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML5 + CSS3 + JavaScript (原生)
- **数据存储**：SQLite（支持从旧 JSON 数据迁移）
- **会话管理**：Flask Session

## 快速开始

### 环境要求

- Python 3.6+
- pip 包管理器

### 安装步骤

1. 克隆项目代码：
```bash
git clone <repository-url>
cd qybs
```

2. 安装依赖：
```bash
pip install flask
```

3. 创建管理员门票文件：
```bash
echo "THIS_IS_A_VERY_SECRET_KEY_FOR_ADMIN_ACCESS_2023" > admin.key
```

4. 启动服务：
```bash
python app.py

# 如需迁移旧 JSON 数据
python migrate_json_to_sqlite.py --clear
```

5. 访问应用：
   - 前台页面：http://localhost:8000
   - 管理后台：http://localhost:8000/admin

### 管理员登录

1. 访问管理后台：http://localhost:8000/admin
2. 点击"上传管理员门票"
3. 选择之前创建的 [admin.key](file://d:\1\project\qybs\admin.key) 文件
4. 验证成功后即可进入管理界面

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

## 安全说明

1. **门票认证**：系统使用基于文件的认证机制，只有持有正确门票文件的用户才能访问管理后台
2. **会话管理**：使用 Flask Session 管理用户登录状态
3. **生产部署**：在生产环境中，请修改 [app.py](file://d:\1\project\qybs\app.py) 中的 `secret_key` 为复杂随机字符串

## 目录结构

```
qybs/
├── app.py                      # 应用入口
├── config.py                   # 路径与配置
├── db.py                       # SQLite 连接与建表
├── routes/                     # 按功能拆分的路由
├── web/                        # 所有 HTML 页面
├── uploads/                    # 上传文件目录
├── migrate_json_to_sqlite.py   # JSON -> SQLite 迁移脚本
└── README.md
```

## 配置说明

在 [app.py](file://d:\1\project\qybs\app.py) 中可以修改以下配置：

- [ADMIN_TICKET_KEY](file://d:\1\project\qybs\app.py#L23-L23)：管理员门票密钥
- [app.secret_key](file://d:\1\project\qybs\app.py#L9-L9)：Flask 应用密钥（生产环境必须修改）
- [UPLOAD_FOLDER](file://d:\1\project\qybs\app.py#L12-L12)：上传文件存储目录
- [DATA_FILE](file://d:\1\project\qybs\app.py#L17-L17)：数据存储文件路径

## 部署建议

### 生产环境部署

1. 修改 [app.secret_key](file://d:\1\project\qybs\app.py#L9-L9) 为强随机字符串
2. 使用 Nginx 或 Apache 作为反向代理
3. 配置 SSL 证书启用 HTTPS
4. 使用 Gunicorn 或 uWSGI 作为应用服务器

