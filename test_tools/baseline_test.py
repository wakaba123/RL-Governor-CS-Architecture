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
from modules.cpuControl import CPUControl,get_swap
from modules.config import *
from modules.getView import *
from modules.get_power import *

view = get_view()

try:
    fps = FPSGet(view=view)
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
    if frame < 60:
        print(colored("Frame: {}".format(frame), "red"))
    frame_data.append(frame)
    sbig_clock = a.get_sbig_cpu_clock()
    big_clock = a.get_big_cpu_clock()
    little_clock = a.get_little_cpu_clock()
    little_util, big_util = a.get_cpu_util_time()
    mem = get_swap()
    print("{}, {}, {}, {}, {}, {}, {}".format(frame, little_util, big_util, little_clock, big_clock,sbig_clock, mem))
    return [frame, little_util, big_util, little_clock, big_clock, sbig_clock, mem]


######################
execute('echo "schedutil" >  /sys/devices/system/cpu/cpufreq/policy0/scaling_governor')  # 恢复为自带调频
execute('echo "schedutil" >  /sys/devices/system/cpu/cpufreq/policy4/scaling_governor')

# execute('echo "1804800" >  /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq')  # 恢复max Frequency
# execute('echo "2419200" >  /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq')

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

with open(test_file_path + "baseline{}.csv".format(version),"w") as f:
       writer = csv.writer(f)
       writer.writerow(things)
# execute('monkey -p com.ss.android.ugc.aweme -c android.intent.category.LAUNCHER 1') # 启动抖音

##### !!!!! important here !!!!!!! ##########
execute('dumpsys batterystats --enable full-wake-history')  # 清除之前的电源信息
execute('dumpsys batterystats --reset')

fps.while_flag = True
fps_thread = Thread(target=fps.get_frame_data_thread, args=())
fps_thread.start()


flag = 1
begin_battery1 = get_charge_cpu()
begin_battery2 = begin_battery1

while flag:
    if begin_battery2 != begin_battery1:
        break
    begin_battery2 = get_charge_cpu()
    print(begin_battery2)
    time.sleep(1)

battery1 = begin_battery2
t1 = datetime.now()


over_last_charge = 0
over_charge = 0

while True:
    print(t)
    m = get_information(cpu)
    if m is None:
        continue

    t = t + 1

    with open(test_file_path + "baseline{}.csv".format(version),"a+") as f:
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

        over_charge = get_charge_cpu()
        print(over_charge)


battery2 = over_charge
t2 = datetime.now()
print(battery1 , battery2)
cost = int(battery2) - int(battery1)
avg_fps = np.mean(frame_data)
print(cost)
print((t2-t1).total_seconds())
fps.while_flag = False
print(frame_data)
print("average FPS : {}".format(sum(frame_data) / len(frame_data)))
second = (t2-t1).total_seconds()
avg_cost = cost / second

os.system(f'echo base,{cost},{avg_fps},{second},{avg_cost} >> {test_file_path}record.csv')  #把记录写到record.csv中

execute('am kill-all')  # 清除所有后台应用
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')
