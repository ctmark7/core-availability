#!/usr/bin/python
import sys
from subprocess import PIPE, Popen 
import re
import os

def main():
    """
    to run:
    python <scriptname.py> <account name>
    return:
    """
    if len(sys.argv) != 2: # add 4th argument for year to exempt? (e.g. 2017?)
        print "\tERROR: Please input valid allocation number"
        print "\tExiting..."
        return -1
    else:
        account = sys.argv[1]
        # print account
        print "Account: {0}".format(account)
        checkAccount(account)
	
	reservations = showRes(account)	
	for res, node_list in reservations.iteritems():
		getJobs(res)	
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
        return False

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
		return res_dict
def getJobs(reservation):
	"""
	input: dict of reservation keys and list of nodes as values
	return: gets info of RUNNING jobs on inputted reservation [JOBID, MHOST, PROCS, STARTTIME(necessary?)]
		currently returns 2D array w/ info on current running jobs for inputted reservation
	"""
	
	cmd = "showq -R {0} -r".format(reservation)
	showq = popen_output(cmd)
	if showq is not None:
		showq = [line.split() for line in showq.split("\n") if line]
		# output format: ['JOBID', 'S', 'PAR', 'EFFIC', 'XFACTOR', 'Q', 'USERNAME', 'ACCNT', 'MHOST', 'PROCS', 'REMAINING', 'STARTTIME']
		jobs = [[line[0], line[8], line[9], line[10]] for line in showq[2:-3]]
		print jobs
	else:
		print "NUTHIN"
	return 0	
def popen_output(cmd):
	p = Popen(cmd, stdout=PIPE,shell=True)
	return p.communicate()[0]

if __name__ == "__main__":
    main()
