import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
WEB_FOLDER = os.path.join(BASE_DIR, 'templates')
NEWS_STYLE_FILE = os.path.join(BASE_DIR, 'news_styles.css')
DB_FILE = os.path.join(BASE_DIR, 'site.db')

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
SECRET_KEY = 'your-very-secret-key-here-change-in-production'
