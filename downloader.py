from yt_dlp import YoutubeDL
import os
import re  # ใช้สำหรับลบอักขระพิเศษ
import browser_cookie3  # ใช้ดึงคุกกี้จากเบราว์เซอร์
import tempfile
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def get_browser_cookies():
    """ดึงคุกกี้จากเบราว์เซอร์ทั้งหมดที่มีและสร้างไฟล์คุกกี้ชั่วคราว"""
    cookies_file = tempfile.mktemp('.txt')
    
    try:
        # ลองดึงคุกกี้จากเบราว์เซอร์ต่างๆ
        all_cookies = []
        
        for browser_name, browser_func in [
            ("Chrome", browser_cookie3.chrome),
            ("Firefox", browser_cookie3.firefox),
            ("Edge", browser_cookie3.edge),
            ("Opera", browser_cookie3.opera),
            ("Safari", browser_cookie3.safari)
        ]:
            try:
                cookies = list(browser_func())
                all_cookies.extend(cookies)
                logger.info(f"พบคุกกี้จาก {browser_name} ({len(cookies)} คุกกี้)")
            except Exception as e:
                logger.debug(f"ไม่สามารถดึงคุกกี้จาก {browser_name}: {str(e)}")
        
        if not all_cookies:
            logger.warning("ไม่พบคุกกี้จากเบราว์เซอร์ใดๆ")
            return None
        
        # แปลงคุกกี้เป็นรูปแบบที่ yt-dlp ใช้ได้
        with open(cookies_file, 'w', encoding='utf-8') as f:
            for cookie in all_cookies:
                # ตรวจสอบว่ามีข้อมูลที่จำเป็นทั้งหมด
                if hasattr(cookie, 'name') and hasattr(cookie, 'value') and hasattr(cookie, 'domain'):
                    f.write(f"{cookie.domain}\tTRUE\t/\tFALSE\t{int(cookie.expires) if hasattr(cookie, 'expires') and cookie.expires else 0}\t{cookie.name}\t{cookie.value}\n")
        
        logger.info(f"สร้างไฟล์คุกกี้ชั่วคราวเรียบร้อย ({len(all_cookies)} คุกกี้)")
        return cookies_file
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในการดึงคุกกี้: {str(e)}")
        return None

def download_video(url, output_format='mp4', output_dir='downloads'):
    """
    ดาวน์โหลดวิดีโอหรือพลายลิสต์จาก YouTube และแหล่งอื่นๆ โดยใช้คุกกี้จากเบราว์เซอร์
    
    Args:
        url (str): URL ของวิดีโอหรือพลายลิสต์
        output_format (str): รูปแบบไฟล์ที่ต้องการ (mp3, mp4 เป็นต้น)
        output_dir (str): โฟลเดอร์ที่จะเก็บไฟล์ที่ดาวน์โหลด
        
    Returns:
        str: เส้นทางไฟล์ที่ดาวน์โหลด
    """
    create_folder(output_dir)
    
    # ดึงคุกกี้จากเบราว์เซอร์อัตโนมัติ
    try:
        # ติดตั้งแพ็คเกจที่จำเป็น (ถ้ายังไม่มี)
        try:
            import browser_cookie3
        except ImportError:
            logger.info("กำลังติดตั้งแพ็คเกจ browser-cookie3")
            import subprocess
            subprocess.call(['pip', 'install', 'browser-cookie3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import browser_cookie3
        
        cookies_path = get_browser_cookies()
    except Exception as e:
        logger.error(f"ไม่สามารถดึงคุกกี้จากเบราว์เซอร์: {str(e)}")
        cookies_path = None
    
    # กำหนดออปชั่นสำหรับ yt-dlp
    ydl_opts = {
        'quiet': True,  # ไม่แสดงข้อความเยอะเกินไป เพื่อให้เหมาะกับการใช้งานเป็น module
        'no_warnings': True,
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
            'format': 'best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        })
    
    # เพิ่มออปชั่นสำหรับ Windows
    ydl_opts['windowsfilenames'] = True
    
    # เพิ่ม cookies ถ้าดึงมาได้
    if cookies_path:
        ydl_opts['cookiefile'] = cookies_path
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            logger.info(f"เริ่มดาวน์โหลด {url}")
            result = ydl.extract_info(url, download=True)
            
            # คืนค่าที่อยู่ของไฟล์ที่ดาวน์โหลด
            if 'entries' in result:  # กรณีเป็น playlist
                # สำหรับ Flask เราต้องการเพียงไฟล์เดียว (ไฟล์แรกของพลายลิสต์)
                video_info = result['entries'][0]
                if output_format.lower() == 'mp3':
                    file_path = os.path.join(output_dir, f"{sanitize_filename(video_info['title'])}.mp3")
                else:
                    file_path = os.path.splitext(ydl.prepare_filename(video_info))[0] + f".{output_format}"
                logger.info(f"ดาวน์โหลดเสร็จสิ้น: {file_path}")
                return file_path
            else:  # กรณีเป็นวิดีโอเดี่ยว
                if output_format.lower() == 'mp3':
                    file_path = os.path.join(output_dir, f"{sanitize_filename(result['title'])}.mp3")
                else:
                    file_path = os.path.splitext(ydl.prepare_filename(result))[0] + f".{output_format}"
                logger.info(f"ดาวน์โหลดเสร็จสิ้น: {file_path}")
                return file_path
    except Exception as e:
        error_msg = f"ไม่สามารถดาวน์โหลดวิดีโอ: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    finally:
        # ลบไฟล์คุกกี้ชั่วคราวหลังจากใช้งานเสร็จ
        if cookies_path and os.path.exists(cookies_path):
            try:
                os.remove(cookies_path)
                logger.debug("ลบไฟล์คุกกี้ชั่วคราวเรียบร้อย")
            except Exception as e:
                logger.debug(f"ไม่สามารถลบไฟล์คุกกี้ชั่วคราว: {str(e)}")

# เพิ่มโค้ดสำหรับการทดสอบเมื่อรันไฟล์โดยตรง
if __name__ == '__main__':
    print("YouTube Downloader (Command Line Mode)")
    url = input("Enter YouTube URL: ")
    output_format = input("Enter format (mp3/mp4): ").strip().lower()
    output_dir = input("Enter output folder name: ").strip() or "downloads"
    
    print("กำลังดึงคุกกี้จากเบราว์เซอร์...")
    
    try:
        file_path = download_video(url, output_format, output_dir)
        print(f"ดาวน์โหลดเสร็จสิ้น: {file_path}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
