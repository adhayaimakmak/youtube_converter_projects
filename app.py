import os
import time
import threading
from flask import Flask, render_template, request, jsonify, send_file, after_this_request
from downloader import download_video

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])  # เพิ่ม GET ด้วย
def download():
    url = request.values.get('url')  # ใช้ .values เพื่อรองรับทั้ง GET และ POST
    output_format = request.values.get('format')

    if not url or not output_format:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    try:
        # ดาวน์โหลดวิดีโอไปยังโฟลเดอร์ชั่วคราว
        temp_folder = 'temp_downloads'
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        file_path = download_video(url, output_format, temp_folder)
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': f"File not found: {file_path}"})

        # ส่งไฟล์กลับไปยังเบราว์เซอร์เพื่อให้ผู้ใช้ดาวน์โหลด
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def delete_file_later(file_path):
    time.sleep(5)  # หน่วงเวลา 5 วินาที
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

if __name__ == '__main__':
    app.run(debug=True)