import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np

from config import *


vcolor='gray'


df = pd.read_csv(test_file_path+'baseline{}_stress.csv'.format(version))
df2 = pd.read_csv(test_file_path+'testline{}_stress.csv'.format(version))
print(np.mean(df2['fps']))


fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)
ax1.plot(df['lclock'], color='blue', label='LITTLE')
ax1.plot(df['bclock'], color='red', label='big')
ax1.set_ylabel('Schedutil \n Clock_data', size=15)
ax1.set_xlabel('Epoch', size=15)
ax1.grid(True)
ax1.legend(loc='upper left', fontsize=15)
ax1.set_xlim(-1, over_time)


ax2.plot(df2['lclock'], color='blue', label='LITTLE')
ax2.plot(df2['bclock'], color='red', label='big')
ax2.set_ylabel('RL_DVFS \n Clock_data', size=15)
ax2.set_xlabel('Epoch', size=15)
ax2.grid(True)
ax2.legend(loc='upper left', fontsize=15)
ax2.set_xlim(-1, over_time)

plt.axvline(cpu_time, 0, 2.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(mem_time, 0, 2.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(io_time, 0, 2.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.tight_layout()
plt.savefig(test_file_path + "clock"+ str(version) +'_stress.png')

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(4, 1, 1)
ax2 = fig.add_subplot(4, 1, 2)
ax3 = fig.add_subplot(4, 1, 3)
ax4 = fig.add_subplot(4, 1, 4)

ax1.plot(df['power'], linewidth=1, color='blue')
ax1.set_ylabel('Schedutil \n Power (mW)', size=15)
ax1.set_xlabel('Epoch', size=15)
ax1.grid(True)
ax1.set_xlim(-1, over_time)

ax2.plot(df2['power'], linewidth=1, color='blue')
ax2.set_ylabel('RL_DVFS \n Power (mW)', size=15)
ax2.set_xlabel('Epoch', size=15)
ax2.grid(True)
ax2.set_xlim(-1, over_time)


target_fps = 60

ax3.plot(df['fps'], color='orange', alpha=0.5)
ax3.axhline(y=target_fps, xmin=0, xmax=2000, color='red', linestyle='--', alpha=0.5)
ax3.set_ylabel('Schedutil \n FPS', size=15)
ax3.set_xlabel('Epoch', size=15)
ax3.grid(True)
ax3.set_xlim(-1, over_time)

ax4.plot(df2['fps'], color='orange', alpha=0.5)
ax4.axhline(y=target_fps, xmin=0, xmax=2000, color='red', linestyle='--', alpha=0.5)
ax4.set_ylabel('RL_DVFS \n FPS', size=15)
#ax4.set_xticks([0, 500, 1000, 1500, 2000])
ax4.set_xlabel('Epoch', size=15)
ax4.grid(True)
ax4.set_xlim(-1, over_time)

plt.tight_layout()

plt.axvline(cpu_time, 0, 6.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(mem_time, 0, 6.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(io_time, 0, 6.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.savefig(test_file_path + "fps_power"+ str(version) +'_stress.png')


fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)
ax1.plot(df['little'], color='blue', label='baseline')
ax1.plot(df2['little'], color='red', label='testline')
ax1.set_ylabel('LITTLE Utilization', size=15)
ax1.set_xlabel('Epoch', size=15)
ax1.grid(True)
ax1.legend(loc='upper left', fontsize=15)
ax1.set_xlim(-1, over_time)


ax2.plot(df['big'], color='blue', label='baseline')
ax2.plot(df2['big'], color='red', label='testline')
ax2.set_ylabel('Big utilization', size=15)
ax2.set_xlabel('Epoch', size=15)
ax2.grid(True)
ax2.legend(loc='upper left', fontsize=15)
ax2.set_xlim(-1, over_time)

ax3.plot(df['mem'], color='blue', label='baseline')
ax3.plot(df2['mem'], color='red', label='testline')
ax3.set_ylabel('Avaliable memory', size=15)
ax3.set_xlabel('Epoch', size=15)
ax3.grid(True)
ax3.legend(loc='upper left', fontsize=15)
ax3.set_xlim(-1, over_time)

plt.axvline(cpu_time, 0, 4, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(mem_time, 0, 4, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(io_time, 0, 4, color=vcolor, linestyle='dashed', clip_on=False)
plt.tight_layout()
plt.savefig(test_file_path + "utilization"+ str(version) +'_stress.png')

'''
lines = [cpu_time,mem_time,io_time,over_time]
for i, thing in enumerate(things):
	fig = plt.figure(figsize=(12,14))
	ax1 = fig.add_subplot(2, 1, 1)
	ax2 = fig.add_subplot(2, 1, 2)
	for line in lines:
		plt.axvline(line,ls='-.',color='g')
	if thing == 'lclock' or thing == 'bclock':
		continue
	ax1.plot(df[thing],label='baseline', color='red')
	ax2.plot(df2[thing],label='testline', color='blue')
	plt.title(thing)
	plt.legend()
	plt.savefig(test_file_path + thing + str(version) +'_stress.png')
	plt.show()
'''

df3 = pd.read_csv(test_file_path+'baseline{}_test.csv'.format(version))
df4 = pd.read_csv(test_file_path+'testline{}_test.csv'.format(version))

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)
ax1.plot(df3['lclock'], color='blue', label='LITTLE')
ax1.plot(df3['bclock'], color='red', label='big')
ax1.set_ylabel('Schedutil \n Clock_data', size=15)
ax1.set_xlabel('Epoch', size=15)
ax1.grid(True)
ax1.legend(loc='upper left', fontsize=15)
ax1.set_xlim(-1, over_time)


ax2.plot(df4['lclock'], color='blue', label='LITTLE')
ax2.plot(df4['bclock'], color='red', label='big')
ax2.set_ylabel('RL_DVFS \n Clock_data', size=15)
ax2.set_xlabel('Epoch', size=15)
ax2.grid(True)
ax2.legend(loc='upper left', fontsize=15)
ax2.set_xlim(-1, over_time)

plt.axvline(cpu_time, 0, 2.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(mem_time, 0, 2.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(io_time, 0, 2.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.tight_layout()
plt.savefig(test_file_path + "clock"+ str(version) +'_test.png')

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(4, 1, 1)
ax2 = fig.add_subplot(4, 1, 2)
ax3 = fig.add_subplot(4, 1, 3)
ax4 = fig.add_subplot(4, 1, 4)

ax1.plot(df3['power'], linewidth=1, color='blue')
ax1.set_ylabel('Schedutil \n Power (mW)', size=15)
ax1.set_xlabel('Epoch', size=15)
ax1.grid(True)
ax1.set_xlim(-1, over_time)

ax2.plot(df4['power'], linewidth=1, color='blue')
ax2.set_ylabel('RL_DVFS \n Power (mW)', size=15)
ax2.set_xlabel('Epoch', size=15)
ax2.grid(True)
ax2.set_xlim(-1, over_time)


target_fps = 60

ax3.plot(df3['fps'], color='orange', alpha=0.5)
ax3.axhline(y=target_fps, xmin=0, xmax=2000, color='red', linestyle='--', alpha=0.5)
ax3.set_ylabel('Schedutil \n FPS', size=15)
#ax2.set_yticks([0, 2000, 4000, 6000, 8000])
#ax4.set_xticks([0, 500, 1000, 1500, 2000])
ax3.set_xlabel('Epoch', size=15)
ax3.grid(True)
ax3.set_xlim(-1, over_time)

ax4.plot(df4['fps'], color='orange', alpha=0.5)
ax4.axhline(y=target_fps, xmin=0, xmax=2000, color='red', linestyle='--', alpha=0.5)
ax4.set_ylabel('RL_DVFS \n FPS', size=15)
#ax4.set_xticks([0, 500, 1000, 1500, 2000])
ax4.set_xlabel('Epoch', size=15)
ax4.grid(True)
ax4.set_xlim(-1, over_time)

plt.axvline(cpu_time, 0, 6.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(mem_time, 0, 6.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(io_time, 0, 6.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.tight_layout()
plt.savefig(test_file_path + "fps_power"+ str(version) +'_test.png')

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)
ax1.plot(df3['little'], color='blue', label='baseline')
ax1.plot(df4['little'], color='red', label='testline')
ax1.set_ylabel('LITTLE Utilization', size=15)
ax1.set_xlabel('Epoch', size=15)
ax1.grid(True)
ax1.legend(loc='upper left', fontsize=15)
ax1.set_xlim(-1, over_time)


ax2.plot(df3['big'], color='blue', label='baseline')
ax2.plot(df4['big'], color='red', label='testline')
ax2.set_ylabel('Big utilization', size=15)
ax2.set_xlabel('Epoch', size=15)
ax2.grid(True)
ax2.legend(loc='upper left', fontsize=15)
ax2.set_xlim(-1, over_time)

ax3.plot(df3['mem'], color='blue', label='baseline')
ax3.plot(df4['mem'], color='red', label='testline')
ax3.set_ylabel('Avaliable memory', size=15)
ax3.set_xlabel('Epoch', size=15)
ax3.grid(True)
ax3.legend(loc='upper left', fontsize=15)
ax3.set_xlim(-1, over_time)

plt.axvline(cpu_time, 0, 4.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(mem_time, 0, 4.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.axvline(io_time, 0, 4.3, color=vcolor, linestyle='dashed', clip_on=False)
plt.tight_layout()
plt.savefig(test_file_path + "utilization"+ str(version) +'_test.png')

