#!/usr/bin/python
import sys
import subprocess as p
import json

#Sort using only the 'id' field of the dictionary
def sortfunction(a, b):
	if(a['id'] > b['id']):
		return 1
	if(a['id'] == b['id']):
		return 0
	else: return -1

#Compact an input list; if input list has the id attribute [10, 20, 20, 30, 30, 40, 50, 50, 60], then the output list will have the
#id attribute [ [10], [20, 20], [30, 30], [40], [50, 50], [60] ]
def compact_list(l):
	c = []
	temp = []
	if(len(l) == 0):
		return temp

	temp.append(l[0])
	i = 1
	while (i < len(l)):
		if(l[i]['id'] == temp[-1]['id']):
			temp.append(l[i])
		else:
			c.append(temp)
			temp = []
			temp.append(l[i])
		i += 1
	
	c.append(temp)
	return c

def main(inputfile):
	try:
		f = open(inputfile)
	except IOError:
		print "Unable to open file [" + inputfile + "]"
		return -1

	try:
		suite = json.load(f);
	except ValueError:
		print "Bad JSON file [" + inputfile + "]"
		return -1

	total_success = 0
	total_failure = 0
	total_disabled = 0
	total_outofrange = 0
	for group in suite:
		success = 0
		failure = 0
		disabled = 0
		outofrange = 0
		endsuite = False
		try:
			if(group['disable']):
				print "Disabled: suite=[" + group['class'] + "]"
				continue
		except KeyError:
			pass
		print "Running: suite=[" + group['class'] + "]"
		l = group['commands']
		l.sort(sortfunction)

		try:
			group_low = group['range'][0]
			group_high = group['range'][1]
			filter_range = True
		except KeyError, IndexError:
			filter_range = False	

		cl = compact_list(l)
		for batch in cl: #batch is a list of commands that can be run in parallel.
			if endsuite:
				break
			child_process = []
			for i in batch:
				i['filter'] = False
				try:
					i['disable']
				except KeyError:
					i['disable'] = False
				if(i['disable']):
					disabled += 1
					total_disabled += 1
					print "Disabled: id=[" + str(i['id']) + "] command=[" + i['command'] + "]"
					child_process.append(0)
				elif(filter_range and (i['id'] < group_low or i['id'] > group_high)):
					outofrange += 1
					total_outofrange += 1
					print "OutofRange: id=[" + str(i['id']) + "] [low=" + str(group_low) + "] high=[" + str(group_high) + "]"
					i['filter'] = True
					child_process.append(0)	
				else:
					print "Running: id=[" + str(i['id']) + "] command=[" + i['command'] + "]"
					child_process.append(p.Popen(i['command'], shell=True))
			for j, i in enumerate(batch):
				if(i['disable'] or i['filter']): continue
				try:
					expected = i['success']
				except KeyError:
					expected = 0

				child_process[j].wait()
				retvalue = child_process[j].returncode
				if(retvalue == expected):
					print "Success: id=[" + str(i['id']) + "] command=[" + i['command'] + "]"
					success += 1
					total_success += 1
					try:
						i['onsuccess']
						print "Running onsuccess: id=[" + str(i['id']) + "] command=[" + i['onsuccess'] + "]"
						successnotify = p.Popen(i['onsuccess'], shell=True)
						successnotify.wait()
					except KeyError:
						pass
				else:
					print "Failure: id=[" + str(i['id']) + "] command=[" + i['command'] + "] expected=[" + str(expected) + "] returned=[" + str(retvalue) + "]"
					failure += 1
					total_failure += 1
					#Command failed; Check if the suit has 'stoponfail' attribute set to True. If so, abort. The default value of the attribute is False, which means we don't stop the suite because of the failure of this command. 
					try:
						i['onfail']
						print "Running onfail: id=[" + str(i['id']) + "] command=[" + i['onfail'] + "]"
						failnotify = p.Popen(i['onfail'], shell=True)
						failnotify.wait()
					except KeyError:
						pass
					try:
						stop = group['stoponfail']
					except KeyError:
						stop = False
					if(stop):
						endsuite = True
						print "Stopping because of failure (id=[" + str(i['id']) + "])"
						break

		print "Completed: suite=[" + group['class'] + "]"
		print "Completed: total=[" + str(success + failure + disabled + outofrange) + "] success=[" + str(success) + "] failed=[" + str(failure) + "] disabled=[" + str(disabled) + "] outofrange=[" + str(outofrange) + "]"
	print "Completed: total=[" + str(total_success + total_failure + total_disabled + total_outofrange) + "] success=[" + str(total_success) + "] failed=[" + str(total_failure) + "] disabled=[" + str(total_disabled) + "] total_outofrange=[" + str(total_outofrange) + "]"
	return 0

if __name__ == '__main__':
	if(len(sys.argv) < 2):
		print "Usage: " + sys.argv[0] + " [filename.json]"
		sys.exit(-1)
	else:
		sys.exit(main(sys.argv[1]))
