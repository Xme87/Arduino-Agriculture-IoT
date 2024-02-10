import os
import paho.mqtt.client as mqtt
import csv
from datetime import datetime
import threading
import atexit
import matplotlib
from plot import plot_csv
import requests
import pandas as pd
import time

matplotlib.use('Agg')

# 現在の日付を取得
current_date = datetime.now().strftime('%Y-%m-%d')

# フォルダを作成
folder_path = os.path.join(os.getcwd(), current_date)
os.makedirs(folder_path, exist_ok=True)

# 各ファイルのパス
file_path = {
    'Soil Humidity': os.path.join(folder_path, 'Soil Humidity.csv'),
    'Air Humidity': os.path.join(folder_path, 'Air Humidity.csv'),
    'Air Temperature': os.path.join(folder_path, 'Air Temperature.csv')
}

# スレッドセーフなロックとイベント
lock = threading.Lock()
data_ready = threading.Event()

# MQTTクライアントの作成
client = mqtt.Client()
received_data = {'Soil Humidity': [], 'Air Humidity': [], 'Air Temperature': []}

# メッセージ受信時のコールバック
def on_message(client, userdata, message):
    received_message = message.payload.decode('utf-8')
    print(received_message)
    timestamp = datetime.now()

    with lock:
        topic = message.topic
        send_line_notify(received_message, topic)
        with open(file_path[topic], 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), received_message])
        received_value = float(received_message)
        received_data[topic].append([timestamp, received_value])

        # グラフを描画
        plot_csv(topic, folder_path)
        send_line_image(folder_path, topic)

# LINE Notify による通知
def send_line_notify(notification_message, topic):
    line_notify_token = "***************************"
    line_notify_api = "https://notify-api.line.me/api/notify"

    # httpヘッダー設定
    headers = {"Authorization": f"Bearer {line_notify_token}"}
    data = {"message": f"{topic}: {notification_message}"}
    requests.post(line_notify_api, headers = headers, data = data)

def send_line_image(notification_image, topic):
    line_notify_token = "***************************"
    line_notify_api = "https://notify-api.line.me/api/notify"

    # payload・httpヘッダー設定
    payload = {'message': f'{topic} chart'}
    headers = {'Authorization': 'Bearer ' + line_notify_token}

    # 送信画像設定
    files = {'imageFile': open(os.path.join(notification_image, f'chart_{topic}.png'), "rb")}  # バイナリファイルオープン

    # post実行
    requests.post(line_notify_api, data=payload, headers=headers, files=files)

print('Detection Start.')
client.on_message = on_message
client.connect('127.0.0.1', 7788, 60)
client.subscribe('Soil Humidity')
client.subscribe('Air Humidity')
client.subscribe('Air Temperature')
client.loop_start()

# 終了処理
def exit_handler():
    client.loop_stop()
    client.disconnect()

atexit.register(exit_handler)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
