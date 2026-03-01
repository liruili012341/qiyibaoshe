import os
from flask import Flask, request
from flask.logging import create_logger

from config import SECRET_KEY, UPLOAD_FOLDER
from db import init_db
from routes.ad_routes import ads_bp
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.comment_routes import comments_bp
from routes.discuss_routes import discuss_bp
from routes.download_routes import download_bp
from routes.like_routes import like_bp
from routes.news_routes import news_bp
from routes.pages_routes import pages_bp
from logger import get_logger


app = Flask(__name__)
app.secret_key = SECRET_KEY

# 创建日志记录器
logger = get_logger('app')

# 请求处理日志中间件
@app.before_request
def log_request():
    logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')

# 响应处理日志中间件
@app.after_request
def log_response(response):
    logger.info(f'Response: {request.method} {request.path} {response.status_code}')
    return response

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()
logger.info('Application initialized and database created')

app.register_blueprint(pages_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(news_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(ads_bp)
app.register_blueprint(discuss_bp)
app.register_blueprint(download_bp)
app.register_blueprint(like_bp)
app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
