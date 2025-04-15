document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const result = document.getElementById('result');
    const spinner = document.getElementById('spinner');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        result.innerHTML = '';
        spinner.style.display = 'block';
        progressContainer.style.display = 'block'; // แสดงแถบความคืบหน้า

        const formData = new FormData(form);
        const queryString = new URLSearchParams(formData).toString();

        window.location.href = `/download?${queryString}`;

        // จำลองการอัปเดตแถบความคืบหน้า (แทนที่ด้วยการอัปเดตจริงถ้ามี)
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressBar.style.width = progress + '%';
            progressBar.textContent = progress + '%';

            if (progress >= 100) {
                clearInterval(interval);
                spinner.style.display = 'none';
                result.innerHTML = '✅ ดาวน์โหลดเสร็จสมบูรณ์!';
                progressContainer.style.display = 'none'; // ซ่อนแถบเมื่อโหลดเสร็จ
            }
        }, 1000); // อัปเดตทุก 1 วินาที

        // ปิด spinner หลัง 2 วินาที (พอให้ผู้ใช้เห็นว่าเริ่มโหลดแล้ว)
        setTimeout(() => {
            spinner.style.display = 'none';
            result.innerHTML = '✅ กำลังดาวน์โหลดไฟล์ของคุณ...';
        }, 2000);
    });
});
