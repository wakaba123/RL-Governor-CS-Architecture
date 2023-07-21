import sys
sys.path.append('/home/wakaba/StudioProjects/RL-Governor-CS-Architecture/test_tools/modules')  # NOQA: E402
from modules.commandExec import execute  # NOQA: E402
import time
import numpy as np
import re
import matplotlib.pyplot as plt

server_pid = 30255
client_pid = 22007


def get_mem(pid):
    output = execute(f'cat /proc/{pid}/status')
    lines = output.split('\n')
    rss_anon = re.search(r'RssAnon:\s+(\d+)\s+kB', output)
    rss_file = re.search(r'RssFile:\s+(\d+)\s+kB', output)
    rss_shmem = re.search(r'RssShmem:\s+(\d+)\s+kB', output)

    if rss_anon and rss_file and rss_shmem:
        rss_anon = int(rss_anon.group(1))
        rss_file = int(rss_file.group(1))
        rss_shmem = int(rss_shmem.group(1))

        total_memory = (rss_anon + rss_file + rss_shmem) / 1024
        return total_memory

    return -1


t = 0
mems = []
while t <= 60:
    # 获取 top 输出结果
    print(t)
    time.sleep(0.2)
    mem = get_mem(server_pid)
    mems.append(float(mem))
    t += 1

# 输出平均值
print(
    f'Average mem: {np.mean(mems)}%')
# print(f'Average Memory: {avg_mem}%')

plt.plot(mems, label='Server_mem')

plt.xlabel('Time (seconds)')
plt.ylabel('Percentage')
# plt.ylim()

plt.legend()
plt.show()
