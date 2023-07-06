import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op
from collections import deque
from threading import Thread, Lock
import time

class PowerGet:
	def __init__(self):
		self.power = 0
		self.voltage = 0
		self.current = 0
		self.power_data = []
		self.voltage_data = []
		self.current_data = []

		self.Mon = HVPM.Monsoon()
		self.Mon.setup_usb()

		self.engine = sampleEngine.SampleEngine(self.Mon)
		self.engine.disableCSVOutput()
		self.engine.ConsoleOutput(False)
		self.power_queue = deque(maxlen=500)
		self.power_queue += [1000]
		self.lock = Lock()

	def get_power_data_thread(self):
		while self.while_flag:
			time.sleep(0.5)
			power = self.get_power_data(2500)
			with self.lock:
				self.power_queue += [power]

	def get_power(self):
		return self.power_queue[-1]

	def get_power_data(self, sampleNum):
		#default channel is main current
		power = []
		self.engine.startSampling(sampleNum)
		sample = self.engine.getSamples()
		self.Mon.stopSampling()
		for i in range(len(sample[sampleEngine.channels.MainCurrent])):
			current = sample[sampleEngine.channels.MainCurrent][i]
			voltage = sample[sampleEngine.channels.MainVoltage][i]
			power.append(current * voltage)
		self.power = sum(power) / len(power)

		#self.power = current * voltage
		self.power_data.append(self.power)

		return self.power


	def powerOff(self):
		self.Mon.setVout(0)


