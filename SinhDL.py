import time
import urllib.request
import pandas as detai2
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 1. CẤU HÌNH DANH SÁCH NGUỒN
targets = [
    {"name": "GitHub", "url": "https://github.com", "type": "Quoc te", "count": 50},
    {"name": "W3Schools", "url": "https://www.w3schools.com", "type": "Quoc te", "count": 25},
    {"name": "DaiNam_Univer", "url": "https://ttsinhvien.dainam.edu.vn", "type": "Trong nuoc", "count": 25},
    {"name": "TikTok", "url": "https://www.tiktok.com", "type": "Quoc te", "count": 15},
    {"name": "SoundCloud", "url": "https://soundcloud.com/", "type": "Quoc te", "count": 15},
    {"name": "CodeLearn", "url": "https://codelearn.io/", "type": "Quoc te", "count": 20}
]

du_lieu_list = []
stt = 1
missing_count = 0

print(f"--- Bắt đầu thu thập dữ liệu chi tiết (Mục tiêu: 150 dòng) ---")

for target in targets:
    # Số lượng cần chạy = Mục tiêu ban đầu + Số lượng bị thiếu từ trang trước
    run_count = target['count'] + missing_count
    missing_count = 0 
    print(f"\nĐang lấy dữ liệu từ: {target['name']} (Số mẫu: {run_count})...")
    
    for i in range(run_count):
        try:
            start_time = time.time()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Gửi request
            req = urllib.request.Request(target['url'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                latency = round((time.time() - start_time) * 1000, 2)
                content = response.read()
                size_kb = round(len(content) / 1024, 2)
                
                du_lieu_list.append({
                    "STT": stt,
                    "Dau_thoi_gian": timestamp,
                    "May_chu": target['name'],
                    "Loai_may_chu": target['type'],
                    "Diem_nhan": target['url'],
                    "Phuong_thuc_HTTP": "GET",
                    "Do_tre_ms": latency,
                    "Kich_thuoc_KB": size_kb,
                    "Ma_trang_thai": response.getcode()
                })
                stt += 1
            time.sleep(0.2)
        except Exception as e:
            missing_count += 1 # Lưu lại số lượng lỗi để bù vào trang sau
            print(f"  [!] Lỗi mẫu {i+1} tại {target['name']}: {e}")

# chuyển sang DataFrame
df = detai2.DataFrame(du_lieu_list)

# 2. LÀM SẠCH DỮ LIỆU
print("\n--- LÀM SẠCH DỮ LIỆU ---")
before_rows = len(df)

text_columns = ["May_chu", "Loai_may_chu", "Diem_nhan", "Phuong_thuc_HTTP"]
for column in text_columns:
    if column in df.columns:
        df[column] = df[column].astype(str).str.strip()

df = df.drop_duplicates()
df = df.dropna()

after_rows = len(df)
print(f"Số dòng trước khi làm sạch: {before_rows}")
print(f"Số dòng sau khi làm sạch: {after_rows}")
print(f"Số dòng bị loại bỏ: {before_rows - after_rows}")

# 2. XUẤT FILE EXCEL 
file_name = "TgianPhanHoi_latency.xlsx"
df.to_excel(file_name, index=False)
print(f"\n✅ Đã lưu file thành công: {file_name}")