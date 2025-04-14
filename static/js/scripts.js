// รอให้หน้าเว็บโหลดเสร็จ
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');      // ฟอร์มหลัก
    const result = document.getElementById('result');           // กล่องแสดงผล
    const spinner = document.getElementById('spinner');         // ตัวหมุนโหลด (ถ้ามี)

    form.addEventListener('submit', (e) => {
        e.preventDefault(); // ป้องกันการ submit แบบ default

        result.innerHTML = '';               // ล้างข้อความเดิม
        spinner.style.display = 'block';     // แสดง spinner

        const formData = new FormData(form);             // เก็บค่าจากฟอร์ม
        const queryString = new URLSearchParams(formData).toString();  // แปลงเป็น query string

        // ใช้ window.location.href เพื่อให้ browser เริ่มดาวน์โหลดทันที
        window.location.href = `/download?${queryString}`;

        // ปิด spinner หลัง 2 วินาที (พอให้ผู้ใช้เห็นว่าเริ่มโหลดแล้ว)
        setTimeout(() => {
            spinner.style.display = 'none';
            result.innerHTML = '✅ กำลังดาวน์โหลดไฟล์ของคุณ...';
        }, 2000);
    });
});
