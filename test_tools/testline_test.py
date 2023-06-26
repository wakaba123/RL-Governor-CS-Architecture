import csv
import os
import time
import sys
from termcolor import colored
from threading import Thread
sys.path.append('/home/blues/Desktop/networkTrans/test_tools/modules')
from datetime import datetime
import simpleaudio as sa
import numpy as np

from modules.commandExec import execute
from modules.fpsGet import FPSGet
from modules.cpuControl import CPUControl, get_swap
from modules.config import *
from modules.getView import *
from modules.get_power import *


try:
    fps = FPSGet(view=get_view())
except:
    print('check your view!')

cpu = CPUControl(2)
frame_data = []

def get_information(a):
    global fps
    try:
        frame = fps.get_fps()
    except:
        pass
        return None
    #if frame < 30:
        #frame = 59 
    if frame < 60:
        print(colored("Frame: {}".format(frame), "red"))
    frame_data.append(frame)
    # sbig_clock = a.get_sbig_cpu_clock()
    big_clock = a.get_big_cpu_clock()
    little_clock = a.get_little_cpu_clock()
    little_util, big_util = a.get_cpu_util_time()
    mem = get_swap()
    print("{}, {}, {}, {}, {}, {}".format(frame, little_util, big_util, little_clock, big_clock, mem))
    return [frame, little_util, big_util, little_clock, big_clock, mem]



execute('echo "schedutil" >  /sys/devices/system/cpu/cpufreq/policy0/scaling_governor')  # 恢复为自带调频
execute('echo "schedutil" >  /sys/devices/system/cpu/cpufreq/policy4/scaling_governor')


execute('am kill-all')  # 清除所有后台应用
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')  # 关闭的service

execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')
execute('am stop-service -n "com.example.networktrans/com.example.networktrans.MyService"')

execute('am force-stop com.example.networktrans')  # 关闭app
execute('am force-stop com.example.anomalyapp') 


testline = []

with open(test_file_path + "testline{}.csv".format(version),"w") as f:
        writer = csv.writer(f)
        writer.writerow(things)

execute('dumpsys batterystats --enable full-wake-history')  # 清除之前的电源信息
execute('dumpsys batterystats --reset')
t = 0
over_last_charge = 0
over_charge = 0

fps.while_flag = True
fps_thread = Thread(target=fps.get_frame_data_thread, args=())
fps_thread.start()

flag = 1
begin_battery1 = get_charge_count()
begin_battery2 = begin_battery1

while flag:
    if begin_battery2 != begin_battery1:
        break
    begin_battery2 = get_charge_count()
    print(begin_battery2)
    time.sleep(1)

battery1 = begin_battery2

execute('am start-foreground-service -n "com.example.networktrans/com.example.networktrans.MyService"')  # 启动我们的算法

print('waiting 3 seconds for binary server to start')
time.sleep(3)

now1 = datetime.now()
while True:
    print(t)
    m = get_information(cpu)
    if m is None:
        continue

    t = t + 1
    with open(test_file_path + "testline{}.csv".format(version),"a+") as f:
        writer = csv.writer(f)
        writer.writerow(m)
        

    if t == cpu_time:
        print("*******************************CPU TIME*********************************")
        execute('am force-stop com.example.anomalyapp') 
        execute('am start-foreground-service -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')


    if t == mem_time:
        print("*******************************MEM TIME*********************************")
        execute('am force-stop com.example.anomalyapp') 
        execute('am start-foreground-service -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')

    if t == io_time:
        print("*******************************IO  TIME*********************************")
        execute('am force-stop com.example.anomalyapp') 
        execute('am start-foreground-service -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')

    if t == over_time:
        print("*******************************OVER TIME*********************************")
        execute('am force-stop com.example.anomalyapp') 

    if t > over_time:
        if over_last_charge != over_charge:
            if over_last_charge != 0:
                break
            else:
                over_last_charge = over_charge 

        over_charge = get_charge_count()
        print(over_charge)


battery2 = over_charge


fps.while_flag = False
# battery2 = get_charge_count()

now2 = datetime.now()
cost = int(battery2) - int(battery1)
avg_fps = np.mean(frame_data)
print(cost)
second = (now2-now1).total_seconds()
avg_cost = cost / second

print(frame_data)
print("average FPS : {}".format(sum(frame_data) / len(frame_data)))

# execute('am force-stop com.ss.android.ugc.aweme') 
execute('am force-stop com.example.networktrans') 
execute('am force-stop com.example.anomalyapp') 

execute('am stopservice -n "com.example.networktrans/com.example.networktrans.MyService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')

os.system(f'echo test,{cost},{avg_fps},{second},{avg_cost} >> {test_file_path}record.csv')

def play_notification_sound():
    # 指定音频文件的路径（例如WAV格式）
    audio_file_path = './piano.wav'

    # 加载音频文件
    wave_obj = sa.WaveObject.from_wave_file(audio_file_path)

    # 播放音频文件
    play_obj = wave_obj.play()

    # 等待音频播放完毕
    play_obj.wait_done()

play_notification_sound()