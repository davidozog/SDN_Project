#Attribution: http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
#!/usr/bin/env python

import select
import socket
import sys
import signal
from communication import *
import pdb
import random
import time
import StatPacket
HOST = '128.223.202.213'
PORT = 50009
MSGSIZE=7568
BUFSIZ = 1024
NUMCLIENTS=2
NUMSETS=4
BETA=0.0
UPDATEPROBS=False
ELEMENTSPERSET=150
OFFSET1=0
OFFSET2=0
assert (NUMSETS*ELEMENTSPERSET)%NUMCLIENTS==0
ELEMENTSPERHOST=(NUMSETS*ELEMENTSPERSET)/NUMCLIENTS
class MMP(object):

    def __init__(self, port=3490, backlog=5):
        self.clients = 0
        # Client map
        random.seed(105)
        self.numMatrices=0
        self.clientmap = {}
        self.lastStatistics=None
        self.portToHostDataSet = {}
        self.hostDataToPort= {}
        # Output socket list
        self.numToClient={}
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interestingPorts=[]
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print 'Listening to port',port,'...'
        self.server.listen(backlog)
        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
        self.distributionMap={}
        self.dataSetMap={}
        # CONTROLLER SOCKET
        try:
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as msg:
          s = None
          print 'failed connecting to controller'
        try:
          s.bind((HOST,PORT))
          s.listen(1)
          print 'bound'
        except socket.error as msg:
          s.close()
          s = None
          print 'failed binding to controller'
        if s is None:
          print 'could not open socket'
          sys.exit(1)
        self.controllerSocket=s
        print 'accepting'
        conn, addr = s.accept()
        print 'accepted'
        print addr
        self.controllerSocket=conn
        print self.controllerSocket

        #END CONTROLLER SOCKET
        for i in range(NUMSETS):
            namea=i
            print 'DATASET: '+str(namea)
            self.dataSetMap[namea]=DataSet(name=namea,init=True,size=ELEMENTSPERSET)

    def sighandler(self, signum, frame):
        # Close the server
        print 'Shutting down server...'
        # Close existing client sockets
        for o in self.outputs:
            o.close()

        self.server.close()

    def getname(self, client):

        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return "foo"

    def cleanDict(self,dictionary):
        newDict={}
        for key,v in dictionary.iteritems():
          addr,prt=key
          nkey=(str(addr),prt)
          if prt in self.interestingPorts:
            #print str(key)+','+str(nkey)
            if not newDict.has_key(nkey):
              newDict[nkey]=v
            else:
              newDict[nkey]=newDict[nkey]+dictionary[key]
        if self.lastStatistics is not None:
          for key in self.lastStatistics.keys():
            addr,prt=key
            nkey=(str(addr),prt)
            if(newDict.has_key(nkey)):
              newDict[nkey]=newDict[nkey]-self.lastStatistics[key] 
        
        self.lastStatistics=dictionary
        return newDict 

    def serve(self):

        inputs = [self.server,sys.stdin,self.controllerSocket]
        self.outputs = []
        print self.controllerSocket
        import time
        running = 1
        phase=0
        while running:
            time.sleep(0.01)
            try:
                inputready,outputready,exceptready = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            except socket.error, e:
                break

            for s in inputready:
                if s==self.controllerSocket:
                  #pdb.set_trace()
                  #print 'Received Data From Controller1'
		  print "Controller Data"
                  data=self.controllerSocket.recv(1048576)
                  #pdb.set_trace()
                  
                  #self.controllerSocket.sendall('MMP is alive')
                  if(data):
                    print 'Received Data From Controller2'
                    print 'Size: ' + str(len(data))
                    print '\n'
                  if data:
                    flow_stat_data=unmarshall(data)
                  if isinstance(flow_stat_data,dict):
                    flow_stat_data=self.cleanDict(flow_stat_data)
                    print "\n  Traffic Matrix:\n"
                    sepStr='    '
                    self.numMatrices+=1
                    sys.stdout.write(sepStr)
                    for key in self.hostDataToPort.keys():
                      sys.stdout.write(str(key)+sepStr)
                    sys.stdout.write('\n')  
                    sys.stdout.write(sepStr)
                    #if(self.numMatrices%5==0):
                    #  pdb.set_trace()
                    totalBytes = 0
		    controlBytes = 0
                    for key in range(NUMCLIENTS):
                      sys.stdout.write(str(key)+sepStr)
                      trange=range(NUMSETS)
                      trange.append(-1)
                      for setName in trange:
                        tkey=self.hostDataToPort[(key,setName)]
                        ip,prt=tkey
                        tkey=('10.0.0.1/32' if ip == '10.0.0.1' else '10.0.0.2/32',prt)
                        if(flow_stat_data.has_key(tkey)):
                          sys.stdout.write(str(flow_stat_data[tkey])+sepStr)
                        else:
                          sys.stdout.write('0'+sepStr)
			totalBytes+=flow_stat_data[tkey] if flow_stat_data.has_key(tkey) else 0
			if setName==-1:
			  controlBytes+=flow_stat_data[tkey] if flow_stat_data.has_key(tkey) else 0
                      sys.stdout.write('\n')
                      sys.stdout.write(sepStr)
		    print 'TOTALFLOWAMOUNT:' + str(time.time()-self.startTime)+":"+ str(totalBytes-controlBytes)#TODO: change to DATA FLOW
		    print 'CONTROLCHANNELFLOWAMOUNT:'+str(time.time()-self.startTime)+":"+ str(controlBytes)
		    if(time.time()-self.startTime >120):
			sys.exit(1)
                    sys.stdout.write('\n\n')
                    #return probabilities (horizontal reasoning)
                    returnDistribution={}
                    for key in range(NUMCLIENTS):
                      total=BETA*MSGSIZE
                      returnDistribution[key]={}
                      for setName in range(NUMSETS):
                         tkey=self.hostDataToPort[(0 if key==1 else 1,setName)]
                         ip,prt=tkey
                         tkey=('10.0.0.1/32' if ip == '10.0.0.1' else '10.0.0.2/32',prt)
                         total+=0 if not flow_stat_data.has_key(tkey) else int(flow_stat_data[tkey])
                         total+=BETA*MSGSIZE
                      for setName in range(NUMSETS):
                         tkey=self.hostDataToPort[(0 if key==1 else 1,setName)]
                         ip,prt=tkey
                         tkey=('10.0.0.1/32' if ip == '10.0.0.1' else '10.0.0.2/32',prt)
                         if(total==0):
                            returnDistribution[key][setName]=1.0/NUMSETS
                         else:
                            returnDistribution[key][setName]= BETA*MSGSIZE/total if not flow_stat_data.has_key(tkey)else (BETA*MSGSIZE+1.0*flow_stat_data[tkey])/total
                    for i in range(NUMCLIENTS):
                      toSend=ServerProbabilityUpdateMessage(probId=2,distribution=returnDistribution[i])
                      if UPDATEPROBS: send(self.numToClient[(i+OFFSET2)%2],toSend)
                      print "Return: "+str(returnDistribution[i])      
                    #end return probabilities
                    #accept probabilities (vertical reasoning) ratio
                    #acceptDistribution={}
                    #for setName in range(NUMSETS):
                    #  total=0
                    #  acceptDistribution[setName]={}
                    #  for key in range(NUMCLIENTS):
                    #     tkey=self.hostDataToPort[(0 if key==1 else 1,setName)]
                    #     ip,prt=tkey
                    #     tkey=('10.0.0.1' if ip == '10.0.0.1' else '10.0.0.2',prt)
                    #     total+=0 if not flow_stat_data.has_key(tkey) else int(flow_stat_data[tkey])
                    #  for key in range(NUMCLIENTS):
                    #     tkey=self.hostDataToPort[(key,setName)]
                    #     ip,prt=tkey
                    #     tkey=('10.0.0.1' if ip == '10.0.0.1' else '10.0.0.2',prt)
                    #     acceptDistribution[setName][key]= 0 if not flow_stat_data.has_key(tkey) or total==0 else (1.0*flow_stat_data[tkey])/total
                    #accept probabilities (vertical reasoning) difference
                    acceptDistribution={}
                    for setName in range(NUMSETS):
                      total=BETA*MSGSIZE
                      
                      acceptDistribution[setName]={}
                      for key in range(NUMCLIENTS):
                         tkey=self.hostDataToPort[(key,setName)]
                         ip,prt=tkey
                         tkey=('10.0.0.1/32' if ip == '10.0.0.1' else '10.0.0.2/32',prt)
                         total+=0 if not flow_stat_data.has_key(tkey) else int(flow_stat_data[tkey])
                         total+=BETA*MSGSIZE
                      for key in range(NUMCLIENTS):
                         tkey=self.hostDataToPort[(key,setName)]
                         ip,prt=tkey
			 tkey=(ip+'/32',prt)
                         mySendAmount=total-flow_stat_data[tkey]+BETA*MSGSIZE if flow_stat_data.has_key(tkey) else BETA*MSGSIZE
                         tkey=('10.0.0.1/32' if ip == '10.0.0.1' else '10.0.0.2/32',prt)
                         #print '======DEBUG======'
                         #print 'Key: '+str(key)
                         #print "mySendAmount: "+str(mySendAmount)
                         #print "Total: "+str(total) 
                         #print '======DEBUG======'
                         if(total==0):
                           acceptDistribution[setName][key]=1.0
                         else:
                           acceptDistribution[setName][key]= BETA*MSGSIZE/total if not flow_stat_data.has_key(tkey) or mySendAmount>flow_stat_data[tkey] else 1.0*(BETA*MSGSIZE+flow_stat_data[tkey]-mySendAmount)/total  
                        
                    for c in range (NUMCLIENTS):
                      formattedDist={}
                      for s in range (NUMSETS):
                        formattedDist[s]=acceptDistribution[s][c]
                      if UPDATEPROBS: send(self.numToClient[(c+OFFSET1)%2],ServerProbabilityUpdateMessage(probId=1,distribution=formattedDist))
                      print "Accept: "+str(formattedDist)      
                    #end accept probabilities
                    #print flow_stat_data
                    #import pdb; pdb.set_trace()
                    #flow_stat_data.printData()

                elif s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'mmp: got connection %d from %s' % (client.fileno(), address)
                    # Read the login name
                    cname = receive(client)

                    # Compute client name and send back
                    self.clients += 1
                    #send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)
                    hostAddr,hostPort=address
                    listenMessage=ServerHostListenMessage(listenInfo=hostPort+1,numPorts=NUMSETS+1)
                    self.numToClient[self.clients-1]=client 
                    for i in range (1,NUMSETS+2):
                      self.interestingPorts.append(hostPort+i)
                      if(i<=NUMSETS):
                        self.portToHostDataSet[hostPort+i]=(self.clients-1,self.dataSetMap.values()[i-1].myName)
                        self.hostDataToPort[(self.clients-1,self.dataSetMap.values()[i-1].myName)]=(hostAddr,hostPort+i)
                    self.portToHostDataSet[hostPort+NUMSETS+1]=(self.clients-1,-1)
                    self.hostDataToPort[(self.clients-1,-1)]=(hostAddr,hostPort+NUMSETS+1)
                    print "Sending listen message to client"
                    send(client,listenMessage)
                    print "Sent listen message to client"
                    ackMsg=receive(client)
                    if(self.clients==NUMCLIENTS):
                        if(phase==0):
                          import time
                          time.sleep(0.5)
                          numFree=[]
                          #DISTRIBUTE DATASETS
                          for c in range(NUMCLIENTS):
                              numFree.append(ELEMENTSPERHOST)
                          #pdb.set_trace()
                          for s in range(NUMSETS):
                              for key in self.dataSetMap[s].myElements.keys():
                                t0,t1,t2=self.dataSetMap[s].myElements[key]
                                self.dataSetMap[s].myElements[key]=(s,t1,t2)
                              builtSets=[]
                              for c in range(NUMCLIENTS):
                                  builtSets.append({})
                              for idx in range(ELEMENTSPERSET):
                                  ourLuckyWinner=int(random.random()*NUMCLIENTS)
                                  while(numFree[ourLuckyWinner]<=0):
                                      ourLuckyWinner+=int(random.random()*NUMCLIENTS)
                                      ourLuckyWinner%=NUMCLIENTS
                                  builtSets[ourLuckyWinner][idx]=self.dataSetMap[s].myElements[idx]
                                  numFree[ourLuckyWinner]-=1
                              for setnum in range(NUMCLIENTS):
                                  tempset=DataSet(name=self.dataSetMap[s].myName,init=False,size=ELEMENTSPERHOST,elements=builtSets[setnum])
                                  toSend=ServerRegisterDataSet(name=tempset.myName,elementSet=tempset)
                                  time.sleep(0.5)
                                  send(self.clientmap.keys()[setnum],toSend)
                          #END DISTRIBUTE DATASETS
                          #DISTRIBUTE PROBABILITY DISTRIBUTION
                          oi=0
                          ii=0
		          self.probUniform={0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
		          self.probEven={0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5}

                          for c in self.clientmap.keys():
                              
                              probDist={}
                              sum=0
                              for s in self.dataSetMap.keys():
                                  weight=random.random()
                                  probDist[s]=weight
                                  sum+=weight
                                  ii+=1
                              for s in self.dataSetMap.keys():
                                  probDist[s]=probDist[s]/sum
                              oi+=1
                              high=0.97
                              low=0.01
                              if(oi==1):
                                probDist[0]=high
                                probDist[1]=low
                                probDist[2]=low
                                probDist[3]=low
                              elif(oi==2):
                                probDist[0]=low
                                probDist[1]=low
                                probDist[2]=low
                                probDist[3]=high
			      
                              toSend=ServerProbabilityUpdateMessage(probId=0,distribution=probDist) #0=RequestProbMap
                              send(c,toSend)
				
			      send(c, ServerProbabilityUpdateMessage(probId=1,distribution=self.probEven)) #0=RequestProbMap
			      send(c, ServerProbabilityUpdateMessage(probId=2,distribution=self.probUniform)) #0=RequestProbMap
                          #END DISTRIBUTE PROBABILITY DISTRIBUTIONS
                          phase=1

                          for fromClient in self.clientmap.keys():
                              loop=0
                              for toClient in self.clientmap.keys():
                                  if fromClient!=toClient:
                                      details,toss=self.clientmap[fromClient]
                                      addr,prt=details
                                      prt+=1
                                      details=(addr,prt)
                                      sendme=ServerHostAlertMessage(hostInfo=details,hostName=loop)
                                      print "Alerting "+str(self.clientmap[fromClient])+" to "+str(self.clientmap[toClient])
                                      send(toClient,sendme)
                                      print "Alerted"+str(self.clientmap[fromClient])+" to "+str(self.clientmap[toClient])
                                      time.sleep(3)
                                  else:
                                      loop+=1
                          for toClient in self.clientmap.keys():
                              print "Sending say go"
                            
                              self.startTime=time.time()
                              time.sleep(0.001)
                              send(toClient,ServerSayGoMessage())
                              print "Sent say go"

                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    for toClient in self.clientmap.keys():
                      send(toClient,ServerSayGoMessage())
                else:
                        data = receive(s)



        self.server.close()

if __name__ == "__main__":
    MMP().serve()
