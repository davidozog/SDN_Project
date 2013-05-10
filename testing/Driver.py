from FlowManager import *

import sys
import pdb
def main():

	hostDict={}
        set_a=DataSet("a")
	set_b=DataSet("b")
	host_a=Host([set_a])
	host_b=Host([set_b])
	myGroup=DistributedGroup()
   	myGroup.addHost(host_a)
   	myGroup.addHost(host_b)
	host_a.addSet(set_a)
	host_b.addSet(set_b)
	for i in range(100):
		host_a.send('a',i,host_b)	
	pdb.set_trace()
	
if __name__=="__main__":
	sys.exit(main())
