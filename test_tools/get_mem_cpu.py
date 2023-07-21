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
server_pid = 30255
client_pid = 30778

# 循环获取数据
while t <= 60:
    # 获取 top 输出结果
    print(t)
    output = modules.commandExec.execute(
        f'top -p {client_pid},{server_pid} -b -n 1')
    lines = output.strip().split('\n')

    server_cpu_percent = -1
    server_mem_percent = -1
    client_cpu_percent = -1
    client_mem_percent = -1

    for line in lines[-2:]:
        if line.split()[0] == str(server_pid):
            server_cpu_percent = float(line.split()[8])
            server_mem_percent = float(line.split()[9])

        if line.split()[0] == str(client_pid):
            client_cpu_percent = float(line.split()[8])
            client_mem_percent = float(line.split()[9])

            print(client_cpu_percent)

    # 解析 CPU 使用和内存占用
    # print(server_mem_percent, client_mem_percent)

    # 记录数据
    server_cpu_values.append(server_cpu_percent)
    server_mem_values.append(server_mem_percent)

    client_cpu_values.append(client_cpu_percent)
    client_mem_values.append(client_mem_percent)

    timestamps.append(t)

    # 停止条件：达到指定的统计时长
    t += 1


# 输出平均值
# print(f'Average Memory: {avg_mem}%')
print(np.mean(np.array(client_cpu_values) + np.array(server_cpu_values)))

plt.plot(timestamps, client_cpu_values, label='Client_CPU')
plt.plot(timestamps, server_cpu_values, label='Server_CPU')
plt.plot(timestamps, np.array(client_cpu_values) +
         np.array(server_cpu_values), label='Total_CPU')

plt.xlabel('Time (seconds)')
plt.ylabel('Percentage')

plt.legend()
plt.show()
