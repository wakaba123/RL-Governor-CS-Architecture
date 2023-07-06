import csv
import os
import time
import sys
from termcolor import colored
from threading import Thread
sys.path.append('./modules')
from datetime import datetime
import numpy as np

from modules.commandExec import * 
from modules.fpsGet import FPSGet
from modules.powerGet import PowerGet
from modules.cpuControl import CPUControl, get_swap
from modules.config import *
from modules.getView import *
from modules.get_power import *


power_control = PowerGet()
try:
    fps = FPSGet(view=get_view())
except:
    print('check your view!')

cpu = CPUControl(2)
frame_data = []
power_data = []

def get_information(a):
    global fps
    try:
        frame = fps.get_fps()
        power = power_control.get_power()
    except:
        pass
        return None
    if frame < 60:
        print(colored("Frame: {}".format(frame), "red"))
    frame_data.append(frame)
    power_data.append(power)
    # sbig_clock = a.get_sbig_cpu_clock()
    big_clock = a.get_big_cpu_clock()
    little_clock = a.get_little_cpu_clock()
    little_util, big_util = a.get_cpu_util_time()
    mem = get_swap()
    print("{}, {}, {}, {}, {}, {}, {}".format(frame, power, little_util, big_util, little_clock, big_clock, mem))
    return [frame, little_util, big_util, little_clock, big_clock, mem, power]



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

with open(test_file_path + "testline{}_stress.csv".format(version),"w") as f:
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

power_control.while_flag = True
power_control_thread = Thread(target=power_control.get_power_data_thread, args=())
power_control_thread.start()

'''
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
'''

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
    with open(test_file_path + "testline{}_stress.csv".format(version),"a+") as f:
        writer = csv.writer(f)
        writer.writerow(m)
        

    if t == cpu_time:
        print("*******************************CPU TIME*********************************")
        execute('kill -9 $(pgrep -x stress)')
        execute_bg('/data/local/tmp/stress --cpu 32')


    if t == mem_time:
        print("*******************************MEM TIME*********************************")
        execute('kill -9 $(pgrep -x stress)')
        execute_bg('/data/local/tmp/stress --vm 8 --vm-bytes 256M --vm-keep')

    if t == io_time:
        print("*******************************IO  TIME*********************************")
        execute('kill -9 $(pgrep -x stress)')
        execute_bg('/data/local/tmp/stress --io 8')

    if t == over_time:
        print("*******************************OVER TIME*********************************")
        execute('kill -9 $(pgrep -x stress)')

    if t > over_time:
        break


#battery2 = over_charge


now2 = datetime.now()

fps.while_flag = False
power_control.while_flag = False

avg_power = np.mean(power_data)
avg_fps = np.mean(frame_data)

second = (now2 - now1).total_seconds()

print(frame_data)
print("duration : {}".format(second))
print("average FPS : {}".format(sum(frame_data) / len(frame_data)))
print("average Power : {}".format(sum(power_data) / len(power_data)))

# execute('am force-stop com.ss.android.ugc.aweme') 
execute('am force-stop com.example.networktrans') 
execute('am force-stop com.example.anomalyapp') 

execute('am stopservice -n "com.example.networktrans/com.example.networktrans.MyService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')

os.system(f'echo test,{avg_fps},{avg_power},{second} >> {test_file_path}record.csv')
