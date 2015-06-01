import time
import zmq

import sys

import subprocess
from Queue import Queue

class logger:

	LOG_LEVEL_INFO = 'INFO'
	LOG_LEVEL_DEBUG = 'DEBUG'
	LOG_LEVEL_ERROR = 'ERROR'

	def __init__(self, allow_log_levels = None):

		self.all_log_levels = [ logger.LOG_LEVEL_INFO, logger.LOG_LEVEL_DEBUG, logger.LOG_LEVEL_ERROR ]
		if allow_log_levels:
			self.allow_log_levels = allow_log_levels
		else:
			self.allow_log_levels = self.all_log_levels

	def log(self, log_level, message):

		assert(log_level in self.all_log_levels)
		if log_level in self.allow_log_levels:
			print '%10s : %s' %(log_level, message)

class message_types:

	MESSAGE_TYPE_STATUS_UPDATE = 'STATUS_UPDATE'
	MESSAGE_TYPE_COMMAND = 'COMMAND'
	MESSAGE_TYPE_COMMAND_RESPONSE = 'COMMAND_RESPONSE'
	MESSAGE_TYPE_INITIAL_HELLO = 'INIT_HELLO'
	MESSAGE_TYPE_INITIAL_RESPONSE = 'INIT_RESPONSE'
	MESSAGE_TYPE_SUBMIT_COMMAND_FOR_PROCESSING = 'SUBMIT_COMMAND_FOR_PROCESSING'
	MESSAGE_TYPE_QUERY_COMMAND_PROCESSING_STATUS = 'QUERY_COMMAND_PROCESSING_STATUS'

	def get_initial_response(self, assigned_client_id):

		message = { }

		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_INITIAL_RESPONSE
		message['CLIENT_ID'] = assigned_client_id

		return message

	def get_initial_hello_message(self):

		message = { }

		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_INITIAL_HELLO
		message['CLIENT_ID'] = None

		return message

	STATUS_READY = 'READY'
	STATUS_OK = 'OK'
	STATUS_KEEP_ALIVE = 'KEEP_ALIVE'
	STATUS_ERROR = 'ERROR'
	STATUS_CLOSING = 'CLOSING'

	def get_more_info_from_status_message(self, message):

		assert(self.is_message_of_type(message, message_types.MESSAGE_TYPE_STATUS_UPDATE))
		return message['MORE_INFO']

	def get_status_message(self, node_status, node_id, more_info = { }):

		message = { }

		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_STATUS_UPDATE

		permitted_message_status_values = [ message_types.STATUS_READY, message_types.STATUS_OK, message_types.STATUS_KEEP_ALIVE, message_types.STATUS_ERROR ]
		assert(node_status in permitted_message_status_values)
		message['STATUS'] = node_status
		message['NODE_ID'] = node_id
		message['MORE_INFO'] = more_info

		return message

	COMMAND_TYPE_EXIT = 'COMMAND_EXIT'
	COMMAND_TYPE_EXECUTE = 'COMMAND_EXECUTE'
	COMMAND_TYPE_TEST = 'COMMAND_TEST'
	COMMAND_TYPE_GET_INFO = 'COMMAND_GET_INFO'

	IOCTL_SUBCOMMAND_CLIENT_INFO = 'IOCTL_SUBCOMMAND_CLIENT_INFO'
	IOCTL_SUBCOMMAND_PENDING_COMMANDS_INFO = 'IOCTL_SUBCOMMAND_PENDING_COMMANDS_INFO'

	def get_command_message(self, command, subcommand, node_id, command_details = { }):

		message = { }

		permitted_command_types = [ message_types.COMMAND_TYPE_EXIT, message_types.COMMAND_TYPE_EXECUTE, message_types.COMMAND_TYPE_TEST, message_types.COMMAND_TYPE_GET_INFO ]
		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_COMMAND
		assert(command in permitted_command_types)
		message['COMMAND'] = command
		message['SUBCOMMAND'] = subcommand
		message['NODE_ID'] = node_id
		message['COMMAND_DETAILS'] = command_details

		return message

	def get_command_response_message(self, command, node_id, command_response_details = { }):

		message = { }

		permitted_command_types = [ message_types.COMMAND_TYPE_EXIT, message_types.COMMAND_TYPE_EXECUTE, message_types.COMMAND_TYPE_TEST, message_types.COMMAND_TYPE_GET_INFO ]
		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_COMMAND_RESPONSE
		assert(command in permitted_command_types)
		message['COMMAND'] = command
		message['NODE_ID'] = node_id
		message['COMMAND_RESPONSE_DETAILS'] = command_response_details

		return message

	def get_submit_command_message(self, node_id, command_details = { }):

		message = self.get_command_message(message_types.COMMAND_TYPE_EXECUTE, None, node_id, command_details)
		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_SUBMIT_COMMAND_FOR_PROCESSING
		return message

	def get_query_command_processing_message(self, node_id, command_reference_id):

		message = { }

		message['MESSAGE_TYPE'] = message_types.MESSAGE_TYPE_QUERY_COMMAND_PROCESSING_STATUS
		message['NODE_ID'] = node_id
		message['REFERENCE_ID'] = command_reference_id

		return message

	def get_command_details(self, message):

		assert(self.is_message_of_type(message, message_types.MESSAGE_TYPE_COMMAND) or self.is_message_of_type(message, message_types.MESSAGE_TYPE_SUBMIT_COMMAND_FOR_PROCESSING))
		return message['COMMAND_DETAILS']

	def get_command_response_details(self, message):

		assert(self.is_message_of_type(message, message_types.MESSAGE_TYPE_COMMAND_RESPONSE))
		return message['COMMAND_RESPONSE_DETAILS']

	def is_message_of_type(self, message, message_type):

		return message['MESSAGE_TYPE'] == message_type

class worker_client:

	def __init__(self, logger_obj = None):

		self.port = '6096'
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.socket.connect('tcp://localhost:' + self.port)

		if logger_obj:
			self.logger_obj = logger_obj
		else:
			self.logger_obj = logger()

	def execute_command(self, command_details):

		results_dict = { }
		time_taken = None

		command_to_run = command_details['COMMAND_TO_RUN']
		command_directory = command_details.get('COMMAND_DIRECTORY') 
		command_arguments = command_details['COMMAND_ARGUMENTS']
		sequence_number = command_details['SEQUENCE_NUMBER']

		arguments = []
		if command_directory:
			full_path_to_program = command_directory + '/' + command_to_run
		else:
			full_path_to_program = command_to_run
		arguments.append(full_path_to_program)
		for command_argument in command_arguments:
			arguments.append(str(command_argument))
	
		start_time = time.time()
		command_output = subprocess.check_output(arguments)
		time_taken = time.time() - start_time

		results_dict['SEQUENCE_NUMBER'] = sequence_number
		results_dict['COMMAND_TO_RUN'] = command_to_run
		results_dict['COMMAND_DIRECTORY'] = command_directory
		results_dict['COMMAND_ARGUMENTS'] = command_arguments
		results_dict['COMMAND_OUTPUT'] = command_output
		results_dict['TIME_TAKEN'] = time_taken

		return results_dict

	def start(self):

		default_sleep_interval = 10

		message_types_obj = message_types()

		# Step 0 - Initial hello message
		message = message_types_obj.get_initial_hello_message()
		self.socket.send_json(message)
		response_message = self.socket.recv_json()
		if message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_INITIAL_RESPONSE):
			client_id = response_message['CLIENT_ID']
			self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received initial hello response m=%s' %(response_message))
		else:
			## Unexpected response received from the server
			self.logger_obj.log(logger.LOG_LEVEL_ERROR, 'Unexpected response received from server m=%s' %(response_message))
			return

		while True:

			# Step 1 - Tell the server that the worker is ready
			message = message_types_obj.get_status_message(message_types.STATUS_READY, client_id)
			self.socket.send_json(message)

			# Step 2 - Accept a request from the co-ordinator
			message = self.socket.recv_json()
			if message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_COMMAND):
				# Received a command, now execute it
	
				command = message['COMMAND']
				if command == message_types.COMMAND_TYPE_EXIT:
					return
				elif command == message_types.COMMAND_TYPE_TEST:
					time.sleep(default_sleep_interval)

					response_message = message_types_obj.get_command_response_message(command, client_id)
					self.socket.send_json(response_message)

					response_from_server = self.socket.recv_json()
					self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received response m=[%s]' %(response_from_server))

				elif command == message_types.COMMAND_TYPE_EXECUTE:
					command_details = message_types_obj.get_command_details(message)

					#### Execute the command and fetch the results !!
					command_response_details = self.execute_command(command_details)

					#### Send the results to the server !!
					response_message = message_types_obj.get_command_response_message(command, client_id, command_response_details)
					self.socket.send_json(response_message)

					#### Wait for response from the server !!
					response_from_server = self.socket.recv_json()
					self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received response m=[%s]' %(response_from_server))

			elif message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_STATUS_UPDATE):

				server_status = message['STATUS']
				if server_status == message_types.STATUS_KEEP_ALIVE:
					time.sleep(default_sleep_interval)
					
class controller:

	def __init__(self, logger_obj = None):

		self.port = '6096'
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.socket.connect('tcp://localhost:' + self.port)

		if logger_obj:
			self.logger_obj = logger_obj
		else:
			self.logger_obj = logger()

	def start(self):

		permitted_options = [ 'EXIT', 'GET_CLIENT_INFO', 'GET_PENDING_COMMANDS_INFO' ]

		message_types_obj = message_types()

		# Step 0 - Initial hello message
		message = message_types_obj.get_initial_hello_message()
		self.socket.send_json(message)
		response_message = self.socket.recv_json()
		if message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_INITIAL_RESPONSE):
			client_id = response_message['CLIENT_ID']
			self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received initial hello response m=%s' %(response_message))
		else:
			## Unexpected response received from the server
			self.logger_obj.log(logger.LOG_LEVEL_ERROR, 'Unexpected response received from server m=%s' %(response_message))
			return

		while True:
	
			user_input = raw_input('>> ')
			user_input = user_input.strip()
			
			if user_input not in permitted_options:
				self.logger_obj.log(logger.LOG_LEVEL_ERROR, 'Available options: %s' %(permitted_options))
				continue
			
			if user_input == 'EXIT':
				return
			elif user_input == 'GET_CLIENT_INFO':
				message = message_types_obj.get_command_message(message_types.COMMAND_TYPE_GET_INFO, message_types.IOCTL_SUBCOMMAND_CLIENT_INFO, client_id)
			elif user_input == 'GET_PENDING_COMMANDS_INFO':
				message = message_types_obj.get_command_message(message_types.COMMAND_TYPE_GET_INFO, message_types.IOCTL_SUBCOMMAND_PENDING_COMMANDS_INFO, client_id)

			self.socket.send_json(message)
			response_message = self.socket.recv_json()
			if message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_COMMAND_RESPONSE):
				self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received response m=%s' %(response_message))
			else:
				## Unexpected response received from the server
				self.logger_obj.log(logger.LOG_LEVEL_ERROR, 'Unexpected response received from server m=%s' %(response_message))
				return

class worker_server:

	def __init__(self, logger_obj = None):

		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)

		self.port = '6096'
		self.socket.bind('tcp://*:' + self.port)

		self.server_node_id = 42

		self.next_client_id = 1024
		self.client_id_dict = { }
		self.next_submit_reference_id = 1024
		self.pending_submit_dict = { }
		self.reverse_submit_dict = { }
		self.results_cache_dict = { }

		if logger_obj:
			self.logger_obj = logger_obj
		else:
			self.logger_obj = logger()

		self.work_queue = work_queue()

	def get_initial_client_property_dict(self):

		property_dict = {
			'message_id' : 0,
			'command_id' : 0,
			'last_message_received' : None,
			'previous_message_type' : None
		}

		return property_dict

	def start(self):

		message_types_obj = message_types()

		while True:

			message = self.socket.recv_json()

			if message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_INITIAL_HELLO):
				self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received initial hello message m=%s' %(message))
				response_message = message_types_obj.get_initial_response(self.next_client_id)
				self.client_id_dict[self.next_client_id] = self.get_initial_client_property_dict()
				self.next_client_id += 1

				self.socket.send_json(response_message)

			elif message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_COMMAND):
				self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received command message m=%s' %(message))
				command = message['COMMAND']
				subcommand = message['SUBCOMMAND']
				if(command == message_types.COMMAND_TYPE_GET_INFO):

					if(subcommand == message_types.IOCTL_SUBCOMMAND_CLIENT_INFO):
						command_response_details = { 'CURRENT_CLIENTS' : self.client_id_dict }
					elif(subcommand == message_types.IOCTL_SUBCOMMAND_PENDING_COMMANDS_INFO):
						command_response_details = { 'PENDING_COMMANDS' : self.pending_submit_dict }

				response_message = message_types_obj.get_command_response_message(command, self.server_node_id, command_response_details)
				self.socket.send_json(response_message)

			elif message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_COMMAND_RESPONSE):

				# Client has processed a command and sent a response

				command_response_details = message_types_obj.get_command_response_details(message)	
				self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received command response m=%s' %(message))

				###### 
				client_id = message['NODE_ID']
				reference_id = self.reverse_submit_dict[client_id]
				self.pending_submit_dict[reference_id] = ('DONE', client_id)
				self.results_cache_dict[reference_id] = message

				# Send OK response to the client
				ok_response = message_types_obj.get_status_message(message_types.STATUS_OK, self.server_node_id)
				self.socket.send_json(ok_response)

			elif message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_SUBMIT_COMMAND_FOR_PROCESSING):

				# Router has sent us a request for command processing. Just place this in processing queue.
				self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Received submit_command message m=%s' %(message))

				command_details = message_types_obj.get_command_details(message)
				command_details['REFERENCE_ID'] = reference_id = self.next_submit_reference_id
				self.pending_submit_dict[self.next_submit_reference_id] = ('UNASSIGNED', 0)
				self.next_submit_reference_id += 1

				self.work_queue.put_command_in_queue(command_details)

				more_info_dict = { }
				more_info_dict['REFERENCE_ID'] = reference_id
				# Send OK response to the client
				ok_response = message_types_obj.get_status_message(message_types.STATUS_OK, self.server_node_id, more_info_dict)
				self.socket.send_json(ok_response)
			
			elif message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_QUERY_COMMAND_PROCESSING_STATUS):

				# Router wants to know the status of a previously submitted command. Check the status of the command, and send a response.
				reference_id = message['REFERENCE_ID']
				if reference_id in self.results_cache_dict:
					# Result is present. i.e. processing has finished !
					self.socket.send_json(self.results_cache_dict[reference_id])
					del self.results_cache_dict[reference_id]
				else:
					keepalive_request = message_types_obj.get_status_message(message_types.STATUS_KEEP_ALIVE, self.server_node_id)
					self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Sending keepalive m=%s' %(keepalive_request))
					self.socket.send_json(keepalive_request)

			elif message_types_obj.is_message_of_type(message, message_types.MESSAGE_TYPE_STATUS_UPDATE):

				client_status = message['STATUS']
				if client_status == message_types.STATUS_READY:

					command_details = self.work_queue.get_next_command_to_run()
					if command_details:
						command_request = message_types_obj.get_command_message(message_types.COMMAND_TYPE_EXECUTE, None, self.server_node_id, command_details)
						client_id = message['NODE_ID']
						self.client_id_dict[client_id]['command_id'] += 1
						self.socket.send_json(command_request)

						reference_id = command_details['REFERENCE_ID']
						self.pending_submit_dict[reference_id] = ('PROCESSING', client_id)
						self.reverse_submit_dict[client_id] = reference_id
					else:
						keepalive_request = message_types_obj.get_status_message(message_types.STATUS_KEEP_ALIVE, self.server_node_id)
						self.logger_obj.log(logger.LOG_LEVEL_INFO, 'Sending keepalive m=%s' %(keepalive_request))
						self.socket.send_json(keepalive_request)

class worker_router:

	def test_router(self):

		command_to_run = 'ls'
		command_arguments = [ '-l' ]
		command_directory = None

		command_output = self.start(command_to_run, command_arguments, command_directory)

		print command_output

	def start(self, program_name, arguments_list, directory_path):

		port = '6096'
		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect('tcp://localhost:' + port)

		logger_obj = logger()

		message_types_obj = message_types()

		command_output = None

		# Step 0 - Initial hello message
		message = message_types_obj.get_initial_hello_message()
		socket.send_json(message)
		response_message = socket.recv_json()
		if message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_INITIAL_RESPONSE):
			client_id = response_message['CLIENT_ID']
			logger_obj.log(logger.LOG_LEVEL_INFO, 'Received initial hello response m=%s' %(response_message))
		else:
			## Unexpected response received from the server
			logger_obj.log(logger.LOG_LEVEL_ERROR, 'Unexpected response received from server m=%s' %(response_message))
			return

		command_details = { }
		command_details['COMMAND_TO_RUN'] = program_name
		command_details['COMMAND_DIRECTORY'] = directory_path
		command_details['COMMAND_ARGUMENTS'] = arguments_list
		command_details['SEQUENCE_NUMBER'] = None

		request_message = message_types_obj.get_submit_command_message(client_id, command_details)
		socket.send_json(request_message)

		response_message = socket.recv_json()
		if message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_STATUS_UPDATE):
			more_info_dict = message_types_obj.get_more_info_from_status_message(response_message)
			reference_id = more_info_dict['REFERENCE_ID']
		else:
			## Unexpected response received from the server
			logger_obj.log(logger.LOG_LEVEL_ERROR, 'Unexpected response received from server m=%s' %(response_message))
			return

		default_sleep_interval = 10

		while True:

			status_request_message = message_types_obj.get_query_command_processing_message(client_id, reference_id)
			socket.send_json(status_request_message)

			response_message = socket.recv_json()
			if message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_STATUS_UPDATE):
				server_status = response_message['STATUS']
				if server_status == message_types.STATUS_KEEP_ALIVE:
					time.sleep(default_sleep_interval)
				elif server_status == message_types.STATUS_ERROR:
					break
			elif message_types_obj.is_message_of_type(response_message, message_types.MESSAGE_TYPE_COMMAND_RESPONSE):
				logger_obj.log(logger.LOG_LEVEL_INFO, 'Received command response m=%s' %(response_message))

				response_details = message_types_obj.get_command_response_details(response_message)
				command_output = response_details['COMMAND_OUTPUT']
				break

		return command_output

class work_queue:

	def __init__(self):

		self.command_list = Queue()

	def put_command_in_queue(self, item):

		self.command_list.put(item)

	def get_next_command_to_run(self):

		command_details = None

		if not self.command_list.empty():
			command_details = self.command_list.get()

		return command_details


if __name__ == '__main__':

	type_of_services = [ 'WORKER_SERVER', 'WORKER_CLIENT', 'CONTROLLER', 'ROUTER' ]

	arguments = sys.argv[1:]
	if len(arguments) > 0 and (arguments[0] in type_of_services):

		type_of_service = arguments[0]

		if type_of_service == 'WORKER_SERVER':
			worker_server().start()
		elif type_of_service == 'WORKER_CLIENT':
			worker_client().start()
		elif type_of_service == 'CONTROLLER':
			controller().start()
		elif type_of_service == 'ROUTER':
			worker_router().test_router()

	else:
		print 'Usage: %s %s' %(sys.argv[0], ['|'.join(type_of_services)])
