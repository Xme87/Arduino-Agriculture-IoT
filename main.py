import paho.mqtt.client as mqtt
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import threading
import atexit
import matplotlib

matplotlib.use('Agg')

file_path = {'Soil Humidity': 'Soil Humidity.csv',
             'Air Humidity': 'Air Humidity.csv',
             'Air Temperature': 'Air Temperature.csv'}

lock = threading.Lock()
data_ready = threading.Event()  # 用于通知绘图线程何时开始绘图

client = mqtt.Client()
received_data = {'Soil Humidity': [], 'Air Humidity': [], 'Air Temperature': []}


def on_message(client, userdata, message):
    received_message = message.payload.decode('utf-8')
    print(received_message)
    timestamp = datetime.now()

    with lock:
        topic = message.topic
        with open(file_path[topic], 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), received_message])
        received_value = float(received_message)
        received_data[topic].append([timestamp, received_value])

        # 通知绘图线程开始绘图
        data_ready.set()

print('Detection Start.')
client.on_message = on_message
client.connect('127.0.0.1', 7788, 60)
client.subscribe('Soil Humidity')
client.subscribe('Air Humidity')
client.subscribe('Air Temperature')
client.loop_start()


def plot_chart(topic):
    while True:
        # 等待数据就绪
        data_ready.wait()

        with lock:
            # 按照时间戳对数据进行排序
            sorted_data = sorted(received_data[topic], key=lambda x: x[0])

            # 获取排序后的时间戳和消息
            timestamps = [entry[0] for entry in sorted_data]
            messages = [entry[1] for entry in sorted_data]

            # 绘制图表
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, messages, label=f'{topic}', marker='o')
            plt.title(f'{topic}')
            plt.xlabel('Timestamp')
            plt.ylabel('Value')
            plt.legend()
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
            plt.xticks(rotation=45)
            plt.tight_layout()

            plt.savefig(f'chart_{topic}.png')
            plt.close()


# 注册退出函数
def exit_handler():
    client.loop_stop()
    client.disconnect()


atexit.register(exit_handler)

try:
    while True:
        pass

except KeyboardInterrupt:
    # 用户按下 Ctrl+C 时执行
    threading.Thread(target=plot_chart, args=('Soil Humidity',), daemon=True).start()
    threading.Thread(target=plot_chart, args=('Air Humidity',), daemon=True).start()
    threading.Thread(target=plot_chart, args=('Air Temperature',), daemon=True).start()

    data_ready.set()  # 通知绘图线程开始绘图
    client.loop_stop()
    client.disconnect()