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
	print("{}, {}, {}, {}, {}, {}".format(frame, little_util, big_util, little_clock, big_clock, mem))
	return [frame, little_util, big_util, little_clock, big_clock, mem, power]


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

with open(test_file_path + "baseline{}_test.csv".format(version),"w") as f:
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


now1 = datetime.now()

while True:
	print(t)
	m = get_information(cpu)
	if m is None:
		continue

	t = t + 1

	with open(test_file_path + "baseline{}_test.csv".format(version),"a+") as f:
		writer = csv.writer(f)
		writer.writerow(m)
		

	if t == cpu_time:
		cpu_now = datetime.now()
		print("*******************************CPU TIME*********************************")
		execute('am force-stop com.example.anomalyapp') 
		execute('am start-foreground-service -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')


	if t == mem_time:
		mem_now = datetime.now()
		print("*******************************MEM TIME*********************************")
		execute('am force-stop com.example.anomalyapp') 
		execute('am start-foreground-service -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')

	if t == io_time:
		io_now = datetime.now()
		print("*******************************IO  TIME*********************************")
		execute('am force-stop com.example.anomalyapp') 
		execute('am start-foreground-service -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')

	if t == over_time:
		over_now = datetime.now()
		print("*******************************OVER TIME*********************************")
		execute('am force-stop com.example.anomalyapp') 

	if t > over_time:
		break


now2 = datetime.now()
fps.while_flag = False
power_control.while_flag = False


avg_power = np.mean(power_data)
avg_fps = np.mean(frame_data)
normal_avg_power = np.mean(power_data[0:cpu_time])
normal_avg_fps = np.mean(frame_data[0:cpu_time])
cpu_avg_power = np.mean(power_data[cpu_time:mem_time])
cpu_avg_fps = np.mean(frame_data[cpu_time:mem_time])
mem_avg_power = np.mean(power_data[mem_time:io_time])
mem_avg_fps = np.mean(frame_data[mem_time:io_time])
io_avg_power = np.mean(power_data[io_time:over_time])
io_avg_fps = np.mean(frame_data[io_time:over_time])

second = (now2 - now1).total_seconds()
normal_second = (cpu_now - now1).total_seconds()
cpu_second = (mem_now - cpu_now).total_seconds()
mem_second = (io_now - mem_now).total_seconds()
io_second = (over_now - io_now).total_seconds()

fps_50count = 0
fps_55count = 0
for fps in frame_data:
	if fps < 50:
		fps_50count = fps_50count + 1
	if fps < 55:
		fps_55count = fps_55count + 1



print(frame_data)
print("duration : {}".format(second))
print("normal: {} cpu: {} mem: {} io: {}".format(normal_second, cpu_second, mem_second, io_second))
print("average FPS : {} min FPS : {} count (fps<50) : {} (fps<55) : {}".format(np.mean(frame_data), np.min(frame_data), fps_50count, fps_55count))
print("normal: {} cpu: {} mem: {} io: {}".format(normal_avg_fps, cpu_avg_fps, mem_avg_fps, io_avg_fps))
print("average Power : {}".format(sum(power_data) / len(power_data)))
print("normal: {} cpu: {} mem: {} io: {}".format(normal_avg_power, cpu_avg_power, mem_avg_power, io_avg_power))
os.system(f'echo base,{avg_fps},{avg_power},{second} >> {test_file_path}record.csv')  #把记录写到record.csv中

execute('am kill-all')  # 清除所有后台应用
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.ComputeService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.DownloadService"')
execute('am stopservice -n "com.example.anomalyapp/com.example.anomalyapp.LoadImageService"')
