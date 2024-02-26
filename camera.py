import cv2
import os
import time
from datetime import datetime, timedelta
import requests

def capture_photo():
    # 创建保存照片的文件夹
    photo_folder = 'photos'
    os.makedirs(photo_folder, exist_ok=True)

    # 生成照片文件名（使用当前日期和时间）
    current_time = datetime.now()
    photo_name = current_time.strftime('%Y%m%d') + '.jpg'
    photo_path = os.path.join(photo_folder, photo_name)

    # 使用opencv捕获图像
    cap = cv2.VideoCapture(0)  # 0表示默认摄像头

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return

    cv2.imwrite(photo_path, frame)
    cap.release()

    send_line_photo(photo_path)
    print(f"Photo captured and saved: {photo_path}")

def send_line_photo(photo_path):
    line_notify_token = "tP7I91LaP1youpdO54dD6Kzi3HC56VNtocU4lRxgmFA"
    line_notify_api = "https://notify-api.line.me/api/notify"

    # payload・httpヘッダー設定
    payload = {'message': 'plant photo'}
    headers = {'Authorization': 'Bearer ' + line_notify_token}

    # 送信画像設定
    files = {'imageFile': open(os.path.join(photo_path), "rb")}  # バイナリファイルオープン

    # post実行
    requests.post(line_notify_api, data=payload, headers=headers, files=files)

# 设置每24小时拍摄一次照片
while True:
    capture_photo()
    time.sleep(24 * 60 * 60)  # 等待24小时
