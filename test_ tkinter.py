from tkinter import Tk, filedialog

root = Tk()
root.withdraw()  # ไม่ต้องโชว์หน้าต่างหลัก
folder_path = filedialog.askdirectory(title="เลือกโฟลเดอร์ปลายทาง")
print("Save to:", folder_path)
root.destroy()  # ปิดหน้าต่างหลังจากเลือกเสร็จ