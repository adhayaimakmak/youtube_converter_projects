from yt_dlp import YoutubeDL
import os
import re  # ใช้สำหรับลบอักขระพิเศษ
import tempfile
import logging
import json

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
cookies_path = os.environ.get("COOKIES_PATH")

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

def download_video(url, output_format='mp4', output_dir='downloads'):
    """
    ดาวน์โหลดวิดีโอหรือพลายลิสต์จาก YouTube และแหล่งอื่นๆ
    
    Args:
        url (str): URL ของวิดีโอหรือพลายลิสต์
        output_format (str): รูปแบบไฟล์ที่ต้องการ (mp3, mp4 เป็นต้น)
        output_dir (str): โฟลเดอร์ที่จะเก็บไฟล์ที่ดาวน์โหลด
        
    Returns:
        str: เส้นทางไฟล์ที่ดาวน์โหลด
    """
    create_folder(output_dir)
    
    # กำหนดออปชั่นสำหรับ yt-dlp
    ydl_opts = {
         "cookies": cookies_path,
        'quiet': False,  # เปิดการแสดงข้อความเพื่อช่วยในการ debug
        'no_warnings': False,
        'verbose': True,  # เพิ่มการแสดงข้อมูลโดยละเอียด (สำหรับ debug)
        
        # ตัวเลือกที่ช่วยหลีกเลี่ยงการถูกตรวจจับว่าเป็นบอท
        'extractor_retries': 3,  # พยายามดึงข้อมูลหลายครั้ง
        'fragment_retries': 10,   # พยายามดาวน์โหลด fragment หลายครั้ง
        'retry_sleep_functions': {'extractor': lambda n: 5 * (n+1)},  # รอระหว่างการลองใหม่
        'sleep_interval': 5,      # รอระหว่างการดาวน์โหลดแต่ละรายการ
        
        # ตัวเลือกสำหรับการแก้ไขปัญหา geo-restriction และ age verification
        'geo_verification_proxy': '',  # ทิ้งว่างไว้ หรือใส่ proxy ถ้ามี
        'geo_bypass': True,
        'age_limit': 21,          # ตั้งค่าอายุเพื่อหลีกเลี่ยงข้อจำกัด
        
        # ตัวเลือกเพิ่มเติมสำหรับการป้องกันการจำกัด
        'sleep_interval_requests': 1,  # รอระหว่าง HTTP requests
        'max_sleep_interval': 5,
        
        # ใช้ user-agent ที่คล้ายเบราว์เซอร์ทั่วไป
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
    }
    
    # กำหนดรูปแบบไฟล์ตามที่ผู้ใช้ต้องการ
    if output_format.lower() == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'best[ext=mp4]/best',  # เน้นดาวน์โหลด mp4 หากมี
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        })
    
    # เพิ่มออปชั่นสำหรับ Windows
    ydl_opts['windowsfilenames'] = True
    
    try:
        # ลอง download โดยใช้ค่าเริ่มต้น
        with YoutubeDL(ydl_opts) as ydl:
            logger.info(f"เริ่มดาวน์โหลด {url}")
            try:
                result = ydl.extract_info(url, download=True)
            except Exception as e:
                # ถ้าเกิด error เกี่ยวกับการยืนยันตัวตน
                if "Sign in to confirm" in str(e) or "Please sign in" in str(e) or "bot" in str(e).lower():
                    logger.warning("ถูกตรวจพบว่าเป็น bot, ลองใช้ตัวเลือกเพิ่มเติม...")
                    
                    # เพิ่มตัวเลือกเพื่อพยายามหลีกเลี่ยงการตรวจจับ
                    ydl_opts.update({
                        'skip_download': False,
                        'force_generic_extractor': False,
                        'extract_flat': False,
                        'referer': 'https://www.google.com/',
                        'source_address': '0.0.0.0',  # ใช้ IP address ใดก็ได้สำหรับ source
                    })
                    
                    # ลองอีกครั้งด้วยตัวเลือกใหม่
                    with YoutubeDL(ydl_opts) as ydl2:
                        result = ydl2.extract_info(url, download=True)
                else:
                    # ถ้าเป็น error ประเภทอื่น ให้ส่งต่อไป
                    raise
            
            # คืนค่าที่อยู่ของไฟล์ที่ดาวน์โหลด
            if 'entries' in result:  # กรณีเป็น playlist
                # สำหรับ Flask เราต้องการเพียงไฟล์เดียว (ไฟล์แรกของพลายลิสต์)
                video_info = result['entries'][0]
                if output_format.lower() == 'mp3':
                    file_path = os.path.join(output_dir, f"{sanitize_filename(video_info['title'])}.mp3")
                else:
                    file_path = os.path.splitext(ydl.prepare_filename(video_info))[0] + f".{output_format}"
                
                # ตรวจสอบว่าไฟล์มีอยู่จริง
                if not os.path.exists(file_path):
                    # บางครั้ง extension อาจจะไม่ตรงกับที่ระบุ ลอง .mp4
                    potential_file = os.path.splitext(file_path)[0] + ".mp4"
                    if os.path.exists(potential_file):
                        file_path = potential_file
                
                logger.info(f"ดาวน์โหลดเสร็จสิ้น: {file_path}")
                return file_path
            else:  # กรณีเป็นวิดีโอเดี่ยว
                if output_format.lower() == 'mp3':
                    file_path = os.path.join(output_dir, f"{sanitize_filename(result['title'])}.mp3")
                else:
                    file_path = os.path.splitext(ydl.prepare_filename(result))[0] + f".{output_format}"
                
                # ตรวจสอบว่าไฟล์มีอยู่จริง
                if not os.path.exists(file_path):
                    # บางครั้ง extension อาจจะไม่ตรงกับที่ระบุ ลอง .mp4
                    potential_file = os.path.splitext(file_path)[0] + ".mp4"
                    if os.path.exists(potential_file):
                        file_path = potential_file
                
                logger.info(f"ดาวน์โหลดเสร็จสิ้น: {file_path}")
                return file_path
    except Exception as e:
        error_msg = f"ไม่สามารถดาวน์โหลดวิดีโอ: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

# เพิ่มโค้ดสำหรับการทดสอบเมื่อรันไฟล์โดยตรง
if __name__ == '__main__':
    print("YouTube Downloader (Command Line Mode)")
    url = input("Enter YouTube URL: ")
    output_format = input("Enter format (mp3/mp4): ").strip().lower()
    output_dir = input("Enter output folder name: ").strip() or "downloads"
    
    try:
        file_path = download_video(url, output_format, output_dir)
        print(f"ดาวน์โหลดเสร็จสิ้น: {file_path}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
