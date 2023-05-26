import subprocess
from commandExec import execute
def get_swap():
    results = execute(' '.join([ 'cat', '/proc/meminfo', '|', 'grep', 'MemAvailable']))
    results = results.splitlines()
    mem = int(results[0].split()[1])
    return mem

class CPUControl:
	def __init__(self, core_type):
		# arguments
		self.core_type = core_type
		little_clock_path = "/sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies"
		big_clock_path = "/sys/devices/system/cpu/cpufreq/policy4/scaling_available_frequencies"
		sbig_clock_path = "/sys/devices/system/cpu/cpufreq/policy7/scaling_available_frequencies"
		
		self.little_governor_path = "/sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
		self.big_governor_path = "/sys/devices/system/cpu/cpufreq/policy4/scaling_governor"
		self.sbig_governor_path = "/sys/devices/system/cpu/cpufreq/policy7/scaling_governor"

		self.little_min_freq = "/sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq"
		self.big_min_freq = "/sys/devices/system/cpu/cpufreq/policy4/scaling_min_freq"
		self.sbig_min_freq = "/sys/devices/system/cpu/cpufreq/policy7/scaling_min_freq"
		self.little_max_freq = "/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq"
		self.big_max_freq = "/sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq"
		self.sbig_max_freq = "/sys/devices/system/cpu/cpufreq/policy7/scaling_max_freq"

		self.clock_data = []

		# get root access
		# subprocess.run(['adb' , 'root']) 
		
		#set governor userspace
		# subprocess.run(['adb', 'shell', 'echo', 'userspace', '>', self.little_governor_path + ''])
		# subprocess.run(['adb', 'shell', 'echo', 'userspace', '>', self.big_governor_path + ''])

		# get available freq
		self.little_clock_list = subprocess.check_output(['adb', 'shell', 'cat', little_clock_path]).decode('utf-8')
		self.little_clock_list = self.little_clock_list.split()
		self.big_clock_list = subprocess.check_output(['adb', 'shell', 'cat', big_clock_path]).decode('utf-8')
		self.big_clock_list = self.big_clock_list.split()

		# subprocess.run(['adb', 'shell', 'echo', self.little_clock_list[0], '>', self.little_min_freq+ ''])
		# subprocess.run(['adb', 'shell', 'echo', self.little_clock_list[-1], '>', self.little_max_freq+ ''])
		# self.set_little_cpu_clock(-1)
		# subprocess.run(['adb', 'shell', 'echo', self.big_clock_list[0], '>', self.big_min_freq+ ''])
		# subprocess.run(['adb', 'shell', 'echo', self.big_clock_list[-1], '>', self.big_max_freq+ ''])
		# self.set_big_cpu_clock(-1)

		# if core_type == 3:	# big. Little
		# 	self.sbig_clock_list = subprocess.check_output(['adb', 'shell', 'cat', sbig_clock_path]).decode('utf-8').split()
		# 	subprocess.run(['adb', 'shell', '\"echo', 'userspace', '>', self.sbig_governor_path + '\"'])
		# 	subprocess.run(['adb', 'shell', 'echo', self.sbig_clock_list[0], '>', self.sbig_min_freq+ ''])
		# 	subprocess.run(['adb', 'shell', 'echo', self.sbig_clock_list[-1], '>', self.sbig_max_freq+ ''])
		# 	self.set_sbig_cpu_clock(-1)
		# else:
		# 	self.sbig_clock_list = []

		self.initial_user = []
		self.initial_nice = []
		self.initial_system = []
		self.initial_idle = []
		self.initial_iowait = []
		self.initial_irq = []
		self.initial_softirq = []
		results = execute('cat /proc/stat')
		results = results.splitlines()[1:]
		#print(results)
		for i in range(8):
			self.initial_user.append(int(results[i].split()[1]))
			self.initial_nice.append(int(results[i].split()[2]))
			self.initial_system.append(int(results[i].split()[3]))
			self.initial_idle.append(int(results[i].split()[4]))
			self.initial_iowait.append(int(results[i].split()[5]))
			self.initial_irq.append(int(results[i].split()[6]))
			self.initial_softirq.append(int(results[i].split()[7]))

		'''
		print(self.initial_user)
		print(self.initial_nice)
		print(self.initial_system)
		print(self.initial_idle)
		print(self.initial_iowait)
		print(self.initial_irq)
		print(self.initial_softirq)
		'''

	def set_little_cpu_clock(self, i):
		self.little_clk = i
		little_setspeed_path = "/sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed"
		little_curfreq_path = "/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq"
		if self.core_type == 3:
			subprocess.run(['adb' , 'shell', 'echo', self.little_clock_list[i], '>', self.little_max_freq + ''])
			subprocess.run(['adb' , 'shell', 'echo', self.little_clock_list[i], '>', self.little_min_freq + ''])
		subprocess.run(['adb' , 'shell', 'echo', self.little_clock_list[i], '>', little_setspeed_path + ''])

	def set_big_cpu_clock(self, i):
		self.big_clk = i
		big_setspeed_path = "/sys/devices/system/cpu/cpufreq/policy4/scaling_setspeed"
		big_curfreq_path = "/sys/devices/system/cpu/cpufreq/policy4/scaling_cur_freq"
		if self.core_type == 3:
			subprocess.run(['adb' , 'shell', 'echo', self.big_clock_list[i], '>', self.big_max_freq + ''])
			subprocess.run(['adb' , 'shell', 'echo', self.big_clock_list[i], '>', self.big_min_freq + ''])
		subprocess.run(['adb' , 'shell', 'echo', self.big_clock_list[i], '>', big_setspeed_path + ''])

	def set_sbig_cpu_clock(self, i):
		self.sbig_clk = i
		sbig_setspeed_path = "/sys/devices/system/cpu/cpufreq/policy7/scaling_setspeed"
		if self.core_type == 3:
			subprocess.run(['adb' , 'shell', 'echo', self.sbig_clock_list[i], '>', self.sbig_max_freq + ''])
			subprocess.run(['adb' , 'shell', 'echo', self.sbig_clock_list[i], '>', self.sbig_min_freq + ''])
		sbig_curfreq_path = "/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq"
		subprocess.run(['adb' , 'shell', 'echo', self.sbig_clock_list[i], '>', sbig_setspeed_path + ''])
		


	def get_cpu_util(self):
		util_avgs = subprocess.check_output(['adb', 'shell', 'cat', '/proc/sched_debug', '|', 'grep', '-v', 'autogroup', '|', 'grep', '-A', '14', 'cfs_rq', '|', 'grep', 'util_avg', '|', 'awk', '\'{print $3}\'']).decode('utf-8').splitlines()
		#print(util_avgs)
		util_avg_int = []
		util_avg_int = [int(i) for i in util_avgs]
		#util_avgs = util_avgs.splitlines()
		lc_util = int(sum(util_avg_int[:4]) / 500) * 500 
		bc_util = round(sum(util_avg_int[-4:]), -3)

		lc_max_util = int(max(util_avg_int[:4]) / 200) * 200
		bc_max_util = int(max(util_avg_int[-4:]) / 250) * 250
		#subprocess.run(['adb' , 'shell', 'echo', str(self.little_clock_list[i], 'utf-8'), '>', little_getspeed_path + ''])
		return (lc_max_util, bc_max_util)
	
	def get_cpu_util_time(self):
		curr_user = []
		curr_nice = []
		curr_system = []
		curr_idle = []
		curr_iowait = []
		curr_irq = []
		curr_softirq = []
		self.util_data = []
		results = execute('cat /proc/stat')
		results = results.splitlines()[1:]

		#print(results)
		for i in range(8):
			curr_user.append(int(results[i].split()[1]))
			curr_nice.append(int(results[i].split()[2]))
			curr_system.append(int(results[i].split()[3]))
			curr_idle.append(int(results[i].split()[4]))
			curr_iowait.append(int(results[i].split()[5]))
			curr_irq.append(int(results[i].split()[6]))
			curr_softirq.append(int(results[i].split()[7]))

		#little cluster utilization
		little_util = 0
		big_util = 0
		for i in range(8):
			curr_time = curr_user[i] + curr_nice[i] + curr_system[i] + curr_idle[i] + curr_iowait[i] + curr_irq[i] + curr_softirq[i]
			initial_time = self.initial_user[i] + self.initial_nice[i] + self.initial_system[i] + self.initial_idle[i] + self.initial_iowait[i] + self.initial_irq[i] + self.initial_softirq[i]
			interval = curr_time - initial_time
			cpu_util = ((curr_user[i] + curr_system[i] + curr_nice[i]) - (self.initial_user[i] + self.initial_system[i] + self.initial_nice[i])) / interval
			if i < 4:
				little_util = cpu_util + little_util
			else:
				big_util = cpu_util + big_util

			self.util_data.append(cpu_util)

			#print(cpu_util)

		self.initial_user = curr_user
		self.initial_nice = curr_nice
		self.initial_system = curr_system
		self.initial_idle = curr_idle
		self.initial_iowait = curr_iowait
		self.initial_irq = curr_irq
		self.initial_softirq = curr_softirq
		return (little_util, big_util)

	def get_little_cpu_clock(self):
		little_curfreq_path = "/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq"
		little_cpu_clock = subprocess.check_output(['adb', 'shell', 'cat', little_curfreq_path])
		little_cpu_clock = little_cpu_clock.decode('utf-8')
		return int(little_cpu_clock)
		#subprocess.run(['adb' , 'shell', 'echo', str(self.little_clock_list[i], 'utf-8'), '>', little_getspeed_path + ''])

	def get_big_cpu_clock(self):
		big_curfreq_path = "/sys/devices/system/cpu/cpufreq/policy4/scaling_cur_freq"
		big_cpu_clock = subprocess.check_output(['adb', 'shell', 'cat', big_curfreq_path])
		big_cpu_clock = big_cpu_clock.decode('utf-8')
		return int(big_cpu_clock)
		#subprocess.run(['adb' , 'shell', 'echo', str(self.big_clock_list[i], 'utf-8'), '>', big_getspeed_path + ''])

	def get_sbig_cpu_clock(self):
		sbig_curfreq_path = "/sys/devices/system/cpu/cpufreq/policy7/scaling_cur_freq"
		sbig_cpu_clock = subprocess.check_output(['adb', 'shell', 'cat', sbig_curfreq_path])
		sbig_cpu_clock = sbig_cpu_clock.decode('utf-8')
		return int(sbig_cpu_clock)
		#subprocess.run(['adb' , 'shell', 'echo', str(self.sbig_clock_list[i], 'utf-8'), '>', sbig_getspeed_path + ''])

	def get_cpu_clock(self):
		if self.core_type == 2:
			return (self.get_little_cpu_clock(), self.get_big_cpu_clock())
		else:
			return (self.get_little_cpu_clock(), self.get_big_cpu_clock(), self.get_sbig_cpu_clock())

	def set_governor(self, governor):
		subprocess.run(['adb', 'shell', 'echo', governor, '>', self.little_governor_path + ''])
		subprocess.run(['adb', 'shell', 'echo', governor, '>', self.big_governor_path + ''])
		if self.core_type == 3:	# big. Little
			subprocess.run(['adb', 'shell', '\"echo', governor, '>', self.sbig_governor_path + '\"'])
		
	def get_governor(self):
		return str(subprocess.check_output(['adb', 'shell', 'cat', self.little_governor_path]), 'utf-8')
	
		return 0
