import time
import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""
这是一个工具类，用于打印日志、显示进度条等通用功能
"""

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 创建图表输出目录
if not os.path.exists('charts'):
    os.makedirs('charts')

def progress_bar(progress, total, module_name):
    """显示进度条"""
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    sys.stdout.write(f"\r{module_name} 进度: |{bar}| {percent:.2f}%")
    sys.stdout.flush()
    if progress == total:
        print()

def print_log(message):
    """打印日志信息"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"[{timestamp}] {message}")

def simulate_process(duration, steps, module_name, callback=None):
    """一个耗时过程"""
    interval = duration / steps
    for i in range(steps + 1):
        progress_bar(i, steps, module_name)
        if callback and i > 0:
            callback(i)
        time.sleep(interval)