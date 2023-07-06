from collections import deque
from threading import Thread, Lock
import subprocess
import time
from commandExec import execute 
import re

class FPSGet():
	def __init__(self, view):
		self.view = view
		self.fps = 0
		self.t = 0

		out = execute(' '.join(['dumpsys', 'SurfaceFlinger', '--latency-clear', view]))
		time.sleep(1)
	
		(refresh_period, timestamps) = self.get_frame_data()
		self.base_timestamp = 0
		for timestamp in timestamps:
			if timestamp != 0:
				self.base_timestamp = timestamp
				break
		if self.base_timestamp == 0:
			raise RuntimeError("Initial frame collect failed")

		self.last_timestamp = timestamps[-2]
		self.frame_queue = deque(maxlen=500)
		self.frame_queue += [timestamp for timestamp in timestamps]
		self.lock = Lock()


	def start(self):
		fps_thread = Thread(target=self.get_frame_data_thread, args=())
		fps_thread.start()

	def get_frame_data_thread(self):
		while self.while_flag:
			time.sleep(0.5)
			refresh_period, new_timestamps = self.get_frame_data()
			if len(new_timestamps) <= 120:
				continue
			print("len : {}".format(len(new_timestamps)))
			with self.lock:
				self.frame_queue += [timestamp for timestamp in new_timestamps if timestamp > self.last_timestamp]
			if len(new_timestamps):
					self.last_timestamp = new_timestamps[-1]
			


	def get_fps(self):
		time.sleep(1)
		if self.view is None:
			raise RuntimeError("Fail to get current SurfaceFligner view")
		old_timestamps = []
		# calculate fps in past 1 second
		adjusted_timestamps = []
		with self.lock:
			for index in range(len(self.frame_queue)):
					seconds = self.frame_queue[index]
					seconds -= self.base_timestamp
					if seconds > 1e6: # too large, just ignore
						continue
					adjusted_timestamps.append(seconds)


		from_time = adjusted_timestamps[-1] - 1.0
		fps_count = 0
		for seconds in adjusted_timestamps:
			if seconds > from_time:
				fps_count += 1
		self.fps = min(fps_count, 60)
		return self.fps

	def get_frame_data(self):
		results = execute(' '.join(['dumpsys', 'SurfaceFlinger', '--latency', self.view]))
		results = results.splitlines()

		if not len(results):
			raise RuntimeError("Frame Data is Empty.")
			return -1
		timestamps = []
		nanoseconds_per_second = 1e9
	
		refresh_period = int(results[0]) / nanoseconds_per_second
		pending_fence_timestamp = (1 << 63) - 1		
		
		for line in results[1:]:
			fields = line.split()
			if len(fields) != 3:
				continue
			(start, submitting, submitted) = map(int, fields)
			if submitting == 0:
				continue
			timestamp = int(fields[1])
			if timestamp == pending_fence_timestamp:
				continue
			timestamp /= nanoseconds_per_second
			timestamps.append(timestamp)


		return (refresh_period, timestamps)
