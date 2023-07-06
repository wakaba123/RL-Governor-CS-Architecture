import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np

from config import *



df = pd.read_csv(test_file_path+'baseline{}_stress.csv'.format(version))
df2 = pd.read_csv(test_file_path+'testline{}_stress.csv'.format(version))
print(np.mean(df2['fps']))

lines = [cpu_time,mem_time,io_time,over_time]
for i, thing in enumerate(things):
    fig = plt.figure()
    for line in lines:
        plt.axvline(line,ls='-.',color='g')
    plt.plot(df[thing],label='baseline')
    plt.plot(df2[thing],label='testline')
    plt.title(thing)
    plt.legend()
    plt.savefig(test_file_path + thing + str(version) +'_stress.png')
    plt.show()

df3 = pd.read_csv(test_file_path+'baseline{}_test.csv'.format(version))
df4 = pd.read_csv(test_file_path+'testline{}_test.csv'.format(version))

lines = [cpu_time,mem_time,io_time,over_time]
for i, thing in enumerate(things):
    fig = plt.figure()
    for line in lines:
        plt.axvline(line,ls='-.',color='g')
    plt.plot(df3[thing],label='baseline')
    plt.plot(df4[thing],label='testline')
    plt.title(thing)
    plt.legend()
    plt.savefig(test_file_path + thing + str(version) +'_test.png')
    plt.show()

