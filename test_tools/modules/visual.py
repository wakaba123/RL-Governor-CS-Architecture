import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np

from config import *
version = 5 
# base = 25
# cpu_time = 2 * base 
# mem_time = 4 * base
# io_time = 6 * base
# over_time = 8 * base

df = pd.read_csv(test_file_path+'baseline{}.csv'.format(version))
df2 = pd.read_csv(test_file_path+'testline{}.csv'.format(version))
print(np.mean(df2['fps']))

lines = [cpu_time,mem_time,io_time,over_time]
for i, thing in enumerate(things):
    plt.figure(i)
    for line in lines:
        plt.axvline(line,ls='-.',color='g')
    plt.plot(df[thing],label='baseline')
    plt.plot(df2[thing],label='testline')
    plt.title(thing)
    plt.legend()
    plt.savefig(test_file_path + thing + str(version) +'.png')
    plt.show()
    
