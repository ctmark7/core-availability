#!/usr/bin/python
import sys
from subprocess import PIPE, Popen 
import re
import os

def main():
    """
    to run:
    python <scriptname.py> <account name>
    return: formatted sheet of available nodes to account + how many FREE cores are on each one
    """
    if len(sys.argv) != 2: # add 4th argument for year to exempt? (e.g. 2017?)
        print ">> ERROR: Please input valid account number"
        print ">> Exiting..."
        return -1
    else:
        account = sys.argv[1]
        # print account
        print "Account: {0}".format(account)
        checkAccount(account)
	
	jobs = []
	print ">> Getting reservations..." 
	reservations = showRes(account)	
	print ">> Getting jobs..." 
	for res, node_list in reservations.iteritems():
		curr_jobs = getJobs(res)
		if len(curr_jobs) >= 1:
			jobs += curr_jobs	
	if len(jobs) == 0:
		print ">> No active jobs on account {0}".format(account)
		return -1
	print ">> Checking jobs...".format(reservations)	
	checkJobs(jobs)
    return 0

def checkAccount(acc):
    """
    :param acc: an account number
    :return: boolean - true if netID part of account, false if it is not
    """

    # need to get netID somehow...
    # ask pascal how to get list of members belonging to an account
    cmd = 'echo $USER'
#    pp = Popen(cmd, stdout=PIPE, shell=True)
    # p = Popen(['echo', 'user'], stdout=PIPE)
    netid = popen_output(cmd) 
    print "netID: {0}".format(netid)
    # search for netID in account permissions...

    # #using regex ...
    # cmd = 'id'
    # id = subprocess.check_output(cmd, shell=True)
    # group_str = re.search("^groups=\S+", id)
    # groups = re.findall('\((.*?)\)',group_str)
    #
    # if acc in groups:
    #     member = True
    #

    # using 'checkproject <projectname> command ...'
    cmd = "checkproject {0}".format(acc) 
      
	# ask Pascal about 'admin' allocation and how the permissions/ access to it works
    checkproj = popen_output(cmd) 
    if "Reporting" in checkproj:
        print 'Member of {0}'.format(acc, end='') 
    else:
        print checkproj
	print ">> NEED TO FIGURE OUT WHAT ENTAILS PERMISSION TO AN ACCOUNT"
        return -1 

def showRes(acc):
	"""
	input: allocation num
	return: dictionary of reservationIDs and the nodes it is using... format: {resID: [list of used nodes], ...}
	"""
	cmd = 'showres -n -g | grep {0}'.format(acc)
	res_dict = {}
	node_list = popen_output(cmd)
	if not node_list:
		print "No active nodes on '{0}'\nExiting...".format(acc)
		return res_dict
	else:
		dframe = []
		node_list = node_list.split('\n')
		for line in node_list:
			if line:
				line = line.split()
				dframe.append(line)
		# indices 0 and 2 have the node, and the node+id (nodename.xxxxx)
		for line in dframe:
			node = line[0]
			resid = line[2]
			if resid not in res_dict:
				res_dict[resid] = []
			if node not in res_dict[resid]:
				res_dict[resid].append(node)
		# print "Reservations: {0}".format(res_dict)
		return res_dict
def getJobs(reservation):
	"""
	input: dict of reservation keys and list of nodes as values
	return: gets info of RUNNING jobs on inputted reservation [JOBID, MHOST, PROCS] (starttime?) 
		currently returns 2D array w/ info on current running jobs for inputted reservation
	"""
	cmd = "showq -R {0} -r".format(reservation)
	showq = popen_output(cmd)

	showq = [line.split() for line in showq.split("\n") if line]
	# output format: ['JOBID', 'S', 'PAR', 'EFFIC', 'XFACTOR', 'Q', 'USERNAME', 'ACCNT', 'MHOST', 'PROCS', 'REMAINING', 'STARTTIME']
	jobs = [[line[0], line[8], line[9]] for line in showq[2:-3]]
	num_jobs = len(jobs)
	if num_jobs >= 1:
		print "Jobs running on reservation {0}: {1}".format(reservation, len(jobs))
		return jobs
	else:
		print "No running jobs on reservation '{0}'".format(reservation)
		return jobs
def checkJobs(job_list):
	"""
		input: list of currently running jobs for reservation
		output: data struct taht has all nodes + the number of FREE CORES on each one
	"""
	total_tasks = 0
	free_nodes = {} # {job:proc capacity}
	for job in job_list:
		job_num, node_name, proc_cap = job[0],job[1],int(job[2])
		print '>> Checking job {0}...\n>> starts at {1} - process capacity: {2}'.format(job_num, node_name, proc_cap)
		cmd = "checkjob {0}".format(job_num)
		output = popen_output(cmd)
		if 'ERROR' in output:
			print output
			return -1
		task_count = int(re.search("TaskCount: \d{1,}", output).group(0).split()[1]) # don't need this
		nodes = re.search("Allocated Nodes:\n(.+)", output).group(1)
		print nodes
		print len(parseNodes(nodes))
def parseNodes(nodes):
	"""
		input: nodes in following formats...
		  seen formats:
			qnode[4201-4204]*20    # 20 cores used on EACH node in range (inclusive?) 4201-4204 
			[qhimem0003:24]	      # 24 cores used on qhimem0003
			qnode[4184]*20        # 20 cores used on 4184
			[qnode5056:12][qnode5057:12]
			*** ("node:#", "node[xxx-xxx,xxx,xxx-xxx]  -- '#' signifies the number of currently USED (unavailable) cores
		return: # of FREE cores on each node group, (done by getting number of cores being used on EACH node
	"""
	# format [qnode5056:12][qnode5057:12]
	if nodes.startswith('[') and nodes.endswith(']'):
		vals = re.findall("\[([^]]+)\]", nodes)
		vals = [node.split(':') for node in vals]
	else: # format 'qnode[4201-4204]*20' or 'qnode[4184,4187-4194,4196-4198,4222-4224]*20'
		used_nodes, cores = nodes.split('*')
		name = re.search("(\w+)\[",used_nodes).group(1)
		node_nums = re.search("\[([^]]+)\]", used_nodes).group(1).split(',')
		# print name, node_nums, cores
		vals = [] 
		for num in node_nums:
			if '-' in num: # for ranges (e.g. '4187-4195')
				start, end = num.split('-')
				for i in range(int(start),int(end)+1):
					node = name + str(i)
					vals.append([node,cores])
			else:
				node = name + str(num)
				vals.append([node,cores])
	# should i make it a dict or nah?
	return vals	
def popen_output(cmd):
	p = Popen(cmd, stdout=PIPE,shell=True)
	return p.communicate()[0]

if __name__ == "__main__":
    main()
