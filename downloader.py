from yt_dlp import YoutubeDL
import os
import re  # ใช้สำหรับลบอักขระพิเศษ

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def sanitize_filename(filename, max_length=80):
    """ลบอักขระพิเศษที่ Windows ไม่รองรับและตัดชื่อไฟล์ให้ไม่เกิน max_length"""
    # ลบอักขระที่ไม่รองรับใน Windows
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # ตัดชื่อไฟล์ให้ไม่เกิน max_length
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip()
    return filename

def download_video(url, output_format='mp4', output_dir='downloads', cookies_path=None):
    create_folder(output_dir)

    # ตั้งค่า output template
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'windowsfilenames': True,  # เปิดใช้งานการจัดการชื่อไฟล์สำหรับ Windows
    }

    # 🔐 ถ้ามี cookies.txt ให้เพิ่มเข้าไป
    if cookies_path is None:
          cookies_path = os.environ.get("COOKIES_PATH", "/etc/secrets/cookies") # แก้ไขตำแหน่งไฟล์ cookies

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            # คืนค่าที่อยู่ของไฟล์ที่ดาวน์โหลด
            if 'entries' in result:  # กรณีเป็น playlist
                downloaded_files = [os.path.join(output_dir, sanitize_filename(entry['title']) + f".{output_format}") for entry in result['entries']]
                return downloaded_files[0]  # คืนค่าไฟล์แรกใน playlist
            else:  # กรณีเป็นวิดีโอเดี่ยว
                return os.path.join(output_dir, sanitize_filename(result['title']) + f".{output_format}")
    except Exception as e:
        raise RuntimeError(f"Failed to download video: {e}")

def main():
    print("YouTube Playlist Downloader")
    url = input("Enter YouTube playlist URL: ")
    output_format = input("Enter format (mp3/mp4): ").strip().lower()
    output_dir = input("Enter output folder name: ").strip()

    file_path = download_video(url, output_format, output_dir)
    print(f"Generated file path: {file_path}")
    print("✅ Download complete!")

if __name__ == '__main__':
    while True:
        main()
        cont = input("Do you want to download another playlist? (y/n): ").strip().lower()
        if cont != 'y':
            break
    # ถ้าผู้ใช้ไม่ต้องการดาวน์โหลดอีก ให้ปิดโปรแกรม
    print("Goodbye!")
