import os
import datetime
import random
import string
from config import UPLOAD_FOLDER

def handle_file_upload(files):
    """处理文件上传，返回保存的文件名列表"""
    files_info = []
    for file in files:
        if file and file.filename:
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            extension = os.path.splitext(file.filename)[1]
            new_filename = f"media_{timestamp}_{random_str}{extension}"
            filepath = os.path.join(UPLOAD_FOLDER, new_filename)
            file.save(filepath)
            files_info.append(new_filename)
    return files_info