#Attribution: http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/

import socket
import sys
import select
import time
from communication import *
import pdb
import traceback
import asyncore
import random
import math
BUFSIZ = 1024
MSGSIZE=7568
SLIDINGWINDOW=10
DEBUG = False
#READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_ONLY = select.POLLIN | select.POLLPRI
CONWAITTIME=0.2
COMPWAITTIME=0.2
class Client(object):

    def __init__(self, name, host='127.0.0.1', port=3490,outfile='distributions.txt'):
        self.myRequestProbMap = {}
        self.myAcceptanceProbMap = {}
        self.myReturnProbMap = {}
        self.name = name
        # Quit flag
        self.hostsmap={}
        self.haveRequests=True
        self.processingRequests=True
        self.startTime=0
        self.deltaTime=0
        self.timeThreshold=0.3
        self.slidingWindow=0
	self.dataSetMap={}
	self.startTime=0
        self.flag = False
        self.port = int(port)
        self.host = host
        self.sendSockets={}
        self.iterations = 0
        self.debug=False
        self.gotMyElement=True;
        # Initial prompt
        self.fdmap={}
        self.numToBase={}
        self.prompt='[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host,port))
            #apeprint 'Connected to server@%d' % self.port
            # Send my name..
            send(self.sock,ClientSayEhlo())
            #send(self.sock,'NAME: ' + self.name)
            # Contains client address, set it
            self.prompt="Puppy? "
            self.fdmap[self.sock.fileno()]=self.sock
            self.poller=select.poll()
            self.poller.register(self.sock,READ_ONLY)
            #apeprint "SOCK FD "+str(self.sock.fileno())
        except socket.error, e:
            #apeprint 'problem at 1'
            #apeprint 'Could not connect to server @%d' % self.port
            sys.exit(1)
    def chooseSet(self,distribution):
        r = random.random()
        sum = distribution[distribution.keys()[0]]
        print distribution    
        i = 1
        while(r>(sum-0.0000000001)):
            sum+=distribution[distribution.keys()[i]]
            i+=1
        i-=1
        return distribution.keys()[i]
    def chooseReturn(self,element):
        others=0
	print self.myRequestProbMap
	newDist=self.myReturnProbMap.copy()
	
	name=element[0]
	del newDist[name]
	sum=0
	for key in newDist.keys():
	   sum+=newDist[key]
	for key in newDist.keys():
	   newDist[key]=(newDist[key]/sum) if sum >0 else (1.0/len(newDist.keys())) 
        print newDist	
        numothers=0
	return self.chooseSet(newDist)

    def chooseElement(self, setName):
        r = random.random()
        idx = self.dataSetMap[setName].numElements() * r
        return int(idx)
    def cmdloop(self):
        numRcvd=0
        phase=0
        idle=0
        passNum=0
	parity=0
        while not self.flag:
            try:
                if (phase==1) and ((time.time()%1.0)<0.1): 
	          parity+=1
		  parity=parity%2		 
                  #print self.myRequestProbMap
                  #print 'At pass '+str(passNum)+' I received '+str(numRcvd)+' elements (cumulatively)'
		  if len(self.dataSetMap.keys()) == 4:
		    print "TIME:"+str(time.time()-self.initTime)
                  for key in self.dataSetMap.keys():
		    if len(self.dataSetMap.keys()) == 4:
                      print 'In dataset '+str(key)+':'+str(len(self.dataSetMap[key].myElements.keys()))
		  if len(self.dataSetMap.keys()) == 4:
		    print '=========================================='
                passNum+=1
                sys.stdout.flush()
                inputs = [self.sock]
                # Wait for input from stdin & socket
                #inputready, outputready,exceptrdy = select.poll(inputs, [],[])
                inputready=[]
                ttime=time.time()
                if(ttime-self.startTime>self.timeThreshold):
                  self.processingRequests=not self.processingRequests
                  self.startTime=ttime
                  self.timeThreshold=0.1 if not self.processingRequests else 1.0
                if(self.processingRequests):
                  inputready= self.poller.poll(0.1)
              
                ##apeprint "Foofoofoo???"
                idle+=1
                if ((phase==1) and (self.slidingWindow>=-SLIDINGWINDOW)): #and (self.gotMyElement or not self.haveRequests):
		    
                    choiceSet=self.chooseSet(self.myRequestProbMap)
                    mySet=self.dataSetMap[choiceSet].myName
                    choiceElement=self.chooseElement(mySet)
                    passNum+=1
                    if(not self.dataSetMap[choiceSet].myElements.has_key(choiceElement)):
			self.slidingWindow-=1
			print str(self.slidingWindow) +'!!!!!' 
                        request=ClientRequestDataMessage(dataSet=choiceSet,element=choiceElement)
                        self.gotMyElement=False
                        for key in self.hostsmap.keys():
                            #apeprint "Sending"
                            tkey=self.hostsmap[key]
                            #apeprint(tkey[-1].fileno())
                            peer=tkey[-1].getpeername()
                            tkey[-1].close()
                            tkey[-1]= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.fdmap[tkey[-1].fileno()]=tkey[-1]
                            tkey[-1].connect(peer)
                            #apeprint(tkey[-1].fileno())
                            #hostmap[key][-1].close()
                            send(self.hostsmap[key][-1],request)
                            time.sleep(CONWAITTIME)
                            #time.sleep(CONWAITTIME)
                            #apeprint "Sent off "+str(request)+" to "+str(tkey[-1].getpeername())
                    else:
                      time.sleep(COMPWAITTIME)
                      print 'Cache hit on '+str(self.dataSetMap[choiceSet].myElements[choiceElement])
		      numRcvd+=1
		      passNum+=1
                #if(self.processingRequests) and self.slidingWindow<=5:
                if True:#self.slidingWindow<=SLIDINGWINDOW+5:
                 for ifd,evtype in inputready:
                     if not (evtype & (select.POLLIN | select.POLLPRI)):
                         continue
                     self.haveRequests=True
                     #apeprint "I received any data"
                     idle=0
                     i=self.fdmap[ifd]
                     #apeprint "IFD= "+str(ifd)
                     if(phase%2==0) and (phase>0):
                       pdb.set_trace()
                     if i == self.sock:
                         if DEBUG: print 'S1'
                         #tempsock,toss = self.sock.accept()
                         data = receive(self.sock)
                         if DEBUG: print 'S2'
                         #apeprint data
                         if not data:
                             #apeprint 'Shutting down.'
                             self.flag = True
                             break
                         else:
                             print data
                             if isinstance(data,ServerHostAlertMessage):
                                 hostName=data.myHostName
                                 data=data.myHostInfo
                                 haddr,hport=data
                                 self.numToBase[haddr]=data
                                 self.sendSockets[(haddr)]={}
                                 try:
                                     for i in range(self.numSets):
                                         newsocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                         newsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                         #newsocket.setblocking(0)
                                         self.tport=hport+i
                                         #apeprint "Sending on "+str(haddr)+":"+str(hport+i)
                                         time.sleep(0.001)
                                         newsocket.connect((haddr,hport+i))
                                         #apeprint newsocket
                                         tmsg=ClientSayEhlo()
                                         send(newsocket,tmsg)
                                         self.fdmap[newsocket.fileno()]=newsocket
                                         #self.poller.register(newsocket,READ_ONLY)
                                         self.sendSockets[(haddr)][i if i!=(self.numSets-1) else -1]=newsocket
                                         if(not self.hostsmap.has_key(hostName)):
                                             self.hostsmap[hostName]={}
                                         self.hostsmap[hostName][i if i!=(self.numSets-1) else -1]=newsocket

                                 except socket.error, e:
                                     #apeprint 'problem at 2'
                                     #apeprint 'Could not connect to server @%d' % self.tport
                                    #apeprint '======================='
                                     
                                     tb=traceback.format_exc()
                                     print tb
                                     pdb.set_trace()
                             elif isinstance(data,ServerHostListenMessage):
                                 listenport=data.myListenInfo

                                 self.numSets=data.myNumPorts
                                 self.myListeners=[]
                                 for channel in range(self.numSets):
                                    #apeprint "Listening on "+str(listenport+channel)

                                     listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                     listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                     listensocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                                     #apeprint listensocket
                                     listensocket.bind(('',listenport+channel))
                                     listensocket.listen(5)

                                     self.poller.register(listensocket,READ_ONLY)
                                     self.fdmap[listensocket.fileno()]=listensocket
                                     if channel==self.numSets-1:
                                         self.controlChannel=listensocket
                                     else:
                                         self.myListeners.append(listensocket)
                                     send(self.sock, ClientAck())
                             elif isinstance(data,ServerRegisterDataSet):
                                 #numRcvd+=1
                                 #apeprint "modified my data map"
                                 ds=data.myElements
                                 self.dataSetMap[ds.myName]=ds
                             elif isinstance(data,ServerProbabilityUpdateMessage):
				 at=time.time()
                                 if(data.myProbId==0):
                                  self.myRequestProbMap=data.myDistribution
                                 elif(data.myProbId==1):
                                  self.myAcceptanceProbMap=data.myDistribution
                                 elif(data.myProbId==2):
                                  self.myReturnProbMap=data.myDistribution
				 print "Unpack duration: "+str(time.time()-at)
                             elif isinstance(data,ServerSayGoMessage):
                                 phase=1
                                 self.startTime=time.time()
				 self.initTime=self.startTime
                                 time.sleep(1)
                             #elif isinstance(
                             else:
                                 #apeprint "Unknown packet type from server"
                                 tb=traceback.format_exc()
                                 print tb
                                 pdb.set_trace()

                     elif i==self.controlChannel:
                         #apeprint "Foo?"
                         #if not self.ephemeralSockets.has_key(i):
                         #  self.ephemeralSockets[i]=hostSock
                         hostSock,toss=i.accept()
                         addr,prt=toss
                         #else:
                         #  hostSock=self.ephemeralSockets[i]
                         if DEBUG: print 'C1'
                         data = receive(hostSock)
                         if DEBUG: print 'C2'
                         #apeprint data
                         #apeprint "Moo?"
                         if isinstance(data,ClientRequestDataMessage):
			     passNum+=1
                             dataset=data.myDataSet
                             element=data.myElement
                             response=ClientResponseMessage()
			     self.slidingWindow+=1
                             if(self.dataSetMap[dataset].myElements.has_key(element)):
                                 response.myKeepable=self.dataSetMap[dataset].checkRequests(element)
                                 response.myElement=self.dataSetMap[dataset].myElements[element]
                                 response.myDataSet=self.dataSetMap[dataset].myName
                             #pdb.set_trace()
                             sockToSend=self.sendSockets[addr][dataset]
                             #sockToSend.close()
                             #sockToSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                             bad=True
                             #if not connectionTest:
                             #apeprint "Problem in connection at 207"
                             #  time.sleep(0.001)
                             #  sockToSend.connect(self.mySendSockets[addr][dataset])
                             self.sendSockets[addr][dataset].close()
                             self.sendSockets[addr][dataset]= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                             taddr,tprt=self.numToBase[addr]
                             self.sendSockets[addr][dataset].connect((addr,tprt+dataset))
                             #apeprint (tprt+dataset)
                             self.fdmap[self.sendSockets[addr][dataset].fileno()]=self.sendSockets[addr][dataset]
                             
                             send(self.sendSockets[addr][dataset],response)
                             time.sleep(CONWAITTIME)
                         if isinstance(data,ClientRequestDeletion):
                           
                          #apeprint "Received delete request"
                           dataset=data.myDataSet
                           element=data.myElement
                           if(self.dataSetMap[dataset].myElements.has_key(element)):
                               del self.dataSetMap[dataset].myElements[element]
                               replacement=data.myReplacement
                               name,junk,stuff=replacement
                               if(self.dataSetMap[name].myElements.has_key(junk)):
                                 print "Warning: Error in replacement, received duplicate"
                                 continue
                                 #pdb.set_trace()
                               else:
                                 self.dataSetMap[name].myElements[junk]=replacement
                           else:
                               print "Warning: received request to delete nonexistent element"
                               continue
                         if DEBUG: print 'C3'
                               #pdb.set_trace()
                          #apeprint 'Finished dealing with delete request'+str(dataset)+','+str(element)
                             #apeprint "Done???!?!!!"
                         #hostSock.close()
                     elif i in self.myListeners: #listensocket
                         hostSock, toss = i.accept()
                        #apeprint 'FLIBBERSJKDFHSDKLHSDG' + str(hostSock.getsockname())
                        #apeprint 'SLIBBERSHKSDLFJSDKFSD' + str(hostSock.getpeername())
                         addr,toss2=toss
                         #apeprint "Received packet from other host"
                         #pdb.set_trace()
                         thing3=0
                         if DEBUG: print 'L1'
                         data = receive(hostSock)
                         if DEBUG: print 'L2'
                         if isinstance(data,ClientResponseMessage) and data.myElement!=None:
                           setname,element,value=data.myElement
                           dataset=setname
                           self.gotMyElement=True
                           self.processingRequests=True 
                           #self.slidingWindow+=1
			   #print str(self.slidingWindow) +'!!!!!' 
		           numRcvd+=1
                           print "Receiving totally lemitigate data "+str(data.myElement)
                           if(data.myKeepable):
			     print 'Acc: '+str(self.myAcceptanceProbMap)
                             toKeep=self.myAcceptanceProbMap[setname]
                             #print str(setname)+', TOKEEP '+str(toKeep)
                             if(random.random()<toKeep):
			       print 'Keeping'
                               self.dataSetMap[dataset].myElements[element]=data.myElement
                               bestEffort=0
                               rset=dataset
                               numSets=len(self.dataSetMap.keys())
                               mySet=""
                               keep=True
                               while(rset==dataset) and (bestEffort<1000):
                                 rset=self.dataSetMap[choiceSet].myName
                                 choiceSet=self.chooseReturn(data.myElement)
                                 bestEffort+=1
                               rElement=-1 if rset!=dataset else self.dataSetMap[rset].myElements[self.dataSetMap[rset].myElements.keys()[0] ]
                               while (bestEffort<1000) and (not self.dataSetMap[rset].myElements.has_key(rElement)):
                                 rElement=self.chooseElement(self.dataSetMap[rset].myName)
                                 bestEffort+=1
                               if(self.dataSetMap[rset].myElements.has_key(rElement)): 
                                 replacementElement=self.dataSetMap[rset].myElements[rElement] 
                               else:
                                 print 'Warning: failed to find suitable replacement' 
                                 keep=False
                                 del self.dataSetMap[dataset].myElements[element]
                               print "Replacing with "+str(dataset)+", element "+str(replacementElement)
                               request=ClientRequestDeletion(dataSet=data.myDataSet,element=element,replacement=replacementElement)
                               print passNum
                               if(keep):
                                 self.sendSockets[addr][-1].close()
                                 self.sendSockets[addr][-1]= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                 taddr,tprt=self.numToBase[addr]
                                 self.sendSockets[addr][-1].connect((addr,tprt+self.numSets-1))
                                 self.fdmap[self.sendSockets[addr][-1].fileno()]=self.sendSockets[addr][-1]
                                 send(self.sendSockets[addr][-1],request)
                                 time.sleep(CONWAITTIME)
                                 del self.dataSetMap[rset].myElements[rElement] #DELETE REPLACEMENT
                               print 'Done with delete request'
                         if DEBUG: print 'L3'  
                     else:
                         tb=traceback.format_exc()
                         print tb
                         toss=0
            except KeyboardInterrupt:
                #apeprint 'Interrupted.'
                self.sock.close()
                break
            except socket.error, e:
                #apeprint "Socket error"
                tb=traceback.format_exc()
                print tb
                pdb.set_trace()

if __name__ == "__main__":
    import sys

    if len(sys.argv)<3:
        sys.exit('Usage: %s hostid host portno' % sys.argv[0])

    client = Client(sys.argv[1],sys.argv[2], int(sys.argv[3]))
    client.cmdloop()
