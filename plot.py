import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def plot_csv(filename, folder_path):
    # CSVファイルを読み込む
    df = pd.read_csv(os.path.join(folder_path, f'{filename}.csv'))

    # 最初の列を日付時刻形式に変換
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])

    # 折れ線グラフを描画
    plt.figure(figsize=(10, 6))
    plt.plot(df.iloc[:, 0], df.iloc[:, 1], label=f'{filename}', marker='o')

    # グラフのタイトルとラベルを設定
    plt.title(f'{filename}')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.legend()
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(os.path.join(folder_path, f'chart_{filename}.png'))
    plt.close()
    # グラフを表示
    '''plt.show()'''
