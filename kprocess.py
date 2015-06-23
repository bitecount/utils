import threading
import time
import psutil

class kprocess:

	def __init__(self, config_obj = None):

		self.scheduler_handle = None	

	def at_least_one_cpu_below_threshold(self, cpu_util_list, cpu_sched_threshold):

		for cpu_util in cpu_util_list:
			if cpu_util <= cpu_sched_threshold:
				return True
		return False

	def process_func(self, incoming_func, argument, result_storage, index):

		return_value = incoming_func(argument)
		result_storage[index] = return_value

	def check_if_ready_to_start_new_thread(self):

		## Gather stats for processor, memory and disk utilization
		sleep_interval = 0.2
		cpu_util_list = psutil.cpu_percent(interval = sleep_interval, percpu = True)

		cpu_sched_threshold = 75
		if self.at_least_one_cpu_below_threshold(cpu_util_list, cpu_sched_threshold) and self.index < len(self.argument_list):
			return True
		else:
			return False

	def scheduler_thread(self):

		#### Run the self.process_function for each argument in self.argument_list

		processing_complete = False

		while not processing_complete:

			## Should new threads be started ?
			if self.check_if_ready_to_start_new_thread():

				current_index = self.index

				modified_args_tuple = (self.process_function, self.argument_list[current_index], self.output_list, current_index)
				self.current_thread_pool[current_index] = threading.Thread(target = self.process_func, args = modified_args_tuple)
				self.current_thread_pool[current_index].start()
				self.index += 1

			## Have any threads finished ?
			for unfinished_thread in self.current_thread_pool.keys():

				wait_for_completion_interval = 0
				self.current_thread_pool[unfinished_thread].join(wait_for_completion_interval)
				if(self.current_thread_pool[unfinished_thread].isAlive()):
					pass
				else:
					del self.current_thread_pool[unfinished_thread]

			## Is processing complete ?
			if self.index == len(self.argument_list) and not self.current_thread_pool:
				processing_complete = True

	def wait_for_completion(self):

		if self.scheduler_handle:
			self.scheduler_handle.join()

		output_list = []
		for key in sorted(self.output_list.keys()):
			output_list.append(self.output_list[key])
		return output_list

	def kmap(self, process_function, argument_list):

		self.process_function = process_function
		self.argument_list = argument_list
		self.index = 0

		self.current_thread_pool = { }
		self.output_list = { }

		self.scheduler_handle = threading.Thread(target = self.scheduler_thread)
		self.scheduler_handle.start()
		
		return None

def sample_expensive_compute(x):

	print 'start sample_expensive_compute for x=%s' %(x)
	time.sleep(x)
	print 'done  sample_expensive_compute for x=%s' %(x)
	return x * x

def test_kprocess():

	kprocess_obj = kprocess()

	argument_list = range(25)
	kprocess_obj.kmap(sample_expensive_compute, argument_list)

	output_list = kprocess_obj.wait_for_completion()

	print output_list

if __name__ == '__main__':

	test_kprocess()
