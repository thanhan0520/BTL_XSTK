import time
import urllib.request
import pandas as pd
from datetime import datetime

# Cấu hình danh sách nguồn
targets = [
    {"name": "GitHub", "url": "https://github.com", "type": "Quoc te", "count": 50},
    {"name": "W3Schools", "url": "https://www.w3schools.com", "type": "Quoc te", "count": 25},
    {"name": "DaiNam_Univer", "url": "https://ttsinhvien.dainam.edu.vn", "type": "Trong nuoc", "count": 25},
    {"name": "TikTok", "url": "https://www.tiktok.com", "type": "Quoc te", "count": 15},
    {"name": "SoundCloud", "url": "https://soundcloud.com/", "type": "Trong nuoc", "count": 15},
    {"name": "CodeLearn", "url": "https://codelearn.io/", "type": "Quoc te", "count": 20}
]

du_lieu_list = []
stt = 1

print(f"Đang thu thập dữ liệu chi tiết cho file Excel...")

for target in targets:
    print(f"Dang lay du lieu tu: {target['name']}...")
    for i in range(target['count']):
        try:
            start_time = time.time()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Thiet lap request
            req = urllib.request.Request(target['url'], headers={'User-Agent': 'Mozilla/5.0'})
            
            # Gui request va lay phan hoi
            with urllib.request.urlopen(req, timeout=15) as response:
                latency = round((time.time() - start_time) * 1000, 2)
                # Lay kich thuoc (KB)
                content = response.read()
                size_kb = round(len(content) / 1024, 2)
                status_code = response.getcode()
                method = "GET" # Phuong thuc mac dinh cua urlopen

            du_lieu_list.append({
                "STT": stt,
                "Dau_thoi_gian": timestamp,
                "May_chu": target['name'],
                "Loai_may_chu": target['type'],
                "Diem_nhan": target['url'],
                "Phuong_thuc_HTTP": method,
                "Do_tre_ms": latency,
                "Kich_thuoc_KB": size_kb,
                "Ma_trang_thai": status_code
            })
            
            print(f"  [{target['name']}] Mau {i+1}: {latency}ms | {size_kb}KB")
            stt += 1
            time.sleep(0.2) # Nghi de tranh bi chan
            
        except Exception as e:
            print(f"  Loi tai {target['name']} mau {i+1}: {e}")

# Xuat ra file Excel
df = pd.DataFrame(du_lieu_list)
file_name = "DuLieu_ChiTiet_BTL.xlsx"
df.to_excel(file_name, index=False)

print("\n" + "="*40)
print(f"HOAN THANH! File '{file_name}' da san sang.")
print(f"Tong so dong thuc te thu thap duoc: {len(df)}")