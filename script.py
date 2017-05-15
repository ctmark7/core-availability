import sys
import subprocess
import re
import os

def main():
    """
    to run:
    python <scriptname.py> <account name>
    return:
    """
    if len(sys.argv) != 2: # add 4th argument for year to exempt? (e.g. 2017?)
        print "\tERROR: Please input valid account number"
        print "\tExiting..."
        return -1
    else:
        account = sys.argv[1]

        print account
        print "Account: {}".format(account)
        checkAccount(account)
    return 0

def checkAccount(acc):
    """
    :param acc: an account number
    :return: boolean - true if netID part of account, false if it is not
    """

    # need to get netID somehow...
    # ask pascal how to get list of members belonging to an account
    cmd = 'echo $USER'
    netid = subprocess.check_output(cmd, shell=True)
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
    # cmd = "checkproject {}".format(acc)
    checkproj = subprocess.check_output(cmd, shell=True)
    if checkproj != "You aren't listed as having access to the project %(project)s":
        print "ACCESS GRANTED I need to maybe go into the actualy retrieval of project data"
        return True
    else:
        print checkproj
        return False


if __name__ == "__main__":
    main()
