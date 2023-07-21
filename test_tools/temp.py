import subprocess
# import psutil
import matplotlib.pyplot as plt
import numpy as np
import time
import modules.commandExec


server_cpu_values = []
server_mem_values = []

client_cpu_values = []
client_mem_values = []

timestamps = []

# 开始时间
t = 0
pid = 27125

# 循环获取数据
while t <= 60:
    # 获取 top 输出结果
    print(t)
    output = modules.commandExec.execute(f'top -p {pid} -b -n 1')
    lines = output.strip().split('\n')

    # 解析 CPU 使用和内存占用
    # server_cpu_percent = float(lines[-1].split()[8])
    # server_mem_percent = float(lines[-1].split()[9])

    # client_cpu_percent = float(lines[-2].split()[8])
    client_mem_percent = float(lines[-1].split()[9])

    # 记录数据
    # server_cpu_values.append(server_cpu_percent)
    # server_mem_values.append(server_mem_percent)

    # client_cpu_values.append(client_cpu_percent)
    client_mem_values.append(client_mem_percent)

    timestamps.append(t)

    # 停止条件：达到指定的统计时长
    t += 1


# 输出平均值
print(f'Average mem: {np.mean( np.array(client_mem_values))}%')
# print(f'Average Memory: {avg_mem}%')

# plt.plot(timestamps,server_mem_values , label='Server_mem')
plt.plot(timestamps,client_mem_values , label='Client_mem')
# plt.plot(timestamps, np.array(client_mem_values), label='Total_mem')

plt.xlabel('Time (seconds)')
plt.ylabel('Percentage')
plt.ylim([0,5])

plt.title(f'Mem Usage for Server and Client')
plt.legend()
plt.show()
