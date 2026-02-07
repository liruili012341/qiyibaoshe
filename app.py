import os
from flask import Flask

from config import SECRET_KEY, UPLOAD_FOLDER
from db import init_db
from routes.ad_routes import ads_bp
from routes.auth_routes import auth_bp
from routes.comment_routes import comments_bp
from routes.discuss_routes import discuss_bp
from routes.download_routes import download_bp
from routes.news_routes import news_bp
from routes.pages_routes import pages_bp


app = Flask(__name__)
app.secret_key = SECRET_KEY

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()

app.register_blueprint(pages_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(news_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(ads_bp)
app.register_blueprint(discuss_bp)
app.register_blueprint(download_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
