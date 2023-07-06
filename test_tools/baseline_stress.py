import csv
import os
import sys
from termcolor import colored
from threading import Thread
import numpy as np
from datetime import datetime
import time
sys.path.append('modules')
from modules.commandExec import *
from modules.fpsGet import FPSGet
from modules.powerGet import PowerGet
from modules.cpuControl import CPUControl,get_swap
from modules.config import *
from modules.getView import *
from modules.get_power import *

view = get_view()

power_control = PowerGet()
try:
    fps = FPSGet(view=view)
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
    big_clock = a.get_big_cpu_clock()
    little_clock = a.get_little_cpu_clock()
    little_util, big_util = a.get_cpu_util_time()
    mem = get_swap()
    print("{}, {}, {}, {}, {}, {}, {}".format(frame, power, little_util, big_util, little_clock, big_clock, mem))
    return [frame, little_util, big_util, little_clock, big_clock, mem, power]


######################
execute('echo "schedutil" >  /sys/devices/system/cpu/cpufreq/policy0/scaling_governor')  # 恢复为自带调频
execute('echo "schedutil" >  /sys/devices/system/cpu/cpufreq/policy4/scaling_governor')


execute('am kill-all')  # 清除所有后台应用
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')  # 清除所有服务
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')
execute('am stopservice -n "com.example.networktrans/com.example.networktrans.MyService"')

execute('am force-stop com.example.networktrans')  #我知道的app
execute('am force-stop com.example.anomalyapp') 
########################


baseline = []
t = 0

with open(test_file_path + "baseline{}_stress.csv".format(version),"w") as f:
       writer = csv.writer(f)
       writer.writerow(things)
# execute('monkey -p com.ss.android.ugc.aweme -c android.intent.category.LAUNCHER 1') # 启动抖音

##### !!!!! important here !!!!!!! ##########
execute('dumpsys batterystats --enable full-wake-history')  # 清除之前的电源信息
execute('dumpsys batterystats --reset')

fps.while_flag = True
fps_thread = Thread(target=fps.get_frame_data_thread, args=())
fps_thread.start()

power_control.while_flag = True
power_control_thread = Thread(target=power_control.get_power_data_thread, args=())
power_control_thread.start()

'''
while flag:
    if begin_battery2 != begin_battery1:
        break
    begin_battery2 = get_charge_count()
    print(begin_battery2)
    time.sleep(1)

battery1 = begin_battery2
'''

t1 = datetime.now()


while True:
    print(t)
    m = get_information(cpu)
    if m is None:
        continue

    t = t + 1

    with open(test_file_path + "baseline{}_stress.csv".format(version),"a+") as f:
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

t2 = datetime.now()
fps.while_flag = False
power_control.while_flag = False

avg_power = np.mean(power_data)
avg_fps = np.mean(frame_data)

second = (t2-t1).total_seconds()

print(frame_data)
print("duration : {}".format(second))
print("average FPS : {}".format(sum(frame_data) / len(frame_data)))
print("average Power : {}".format(sum(power_data) / len(power_data)))


os.system(f'echo base,{avg_fps},{avg_power},{second} >> {test_file_path}record.csv')  #把记录写到record.csv中

execute('am kill-all')  # 清除所有后台应用
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')
