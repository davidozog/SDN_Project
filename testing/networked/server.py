#Attribution: http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
#!/usr/bin/env python
#!/usr/bin/env python

"""

A basic, multiclient 'chat server' using Python's select module
with interrupt handling.

Entering any line of input at the terminal will exit the server.
"""

import select
import socket
import sys
import signal
from communication import *
import pdb
import random
import time
import StatPacket
HOST = '192.168.1.124'
PORT = 50009
BUFSIZ = 1024
NUMCLIENTS=2
NUMSETS=4
ELEMENTSPERSET=150
assert (NUMSETS*ELEMENTSPERSET)%NUMCLIENTS==0
ELEMENTSPERHOST=(NUMSETS*ELEMENTSPERSET)/NUMCLIENTS
class MMP(object):
    """ Simple chat server using select """

    def __init__(self, port=3490, backlog=5):
        self.clients = 0
        # Client map
        random.seed(105)
        self.clientmap = {}
        # Output socket list
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
          print 'you suck'
        try:
          s.bind((HOST,PORT))
          s.listen(1)
          print 'bound'
        except socket.error as msg:
          s.close()
          s = None
          print 'you really suck'
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
            print 'FLIBBERTIGIBBET '+str(namea)+','+str(i)
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
        for key in dictionary.keys():
          if key in self.interestingPorts:
            newDict[key]=dictionary[key]
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
                  data=self.controllerSocket.recv(65536)
                  #pdb.set_trace()
                  
                  #self.controllerSocket.sendall('MMP is alive')
                  if(data):
                    print 'Received Data From Controller2'
                    print str(len(data))
                  if data:
                    flow_stat_data=unmarshall(data)
                  if isinstance(flow_stat_data,dict):
                    flow_stat_data=self.cleanDict(flow_stat_data)
                  print flow_stat_data
                    #import pdb; pdb.set_trace()
                    #flow_stat_data.printData()
                elif s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'chatserver: got connection %d from %s' % (client.fileno(), address)
                    # Read the login name
                    cname = receive(client)

                    # Compute client name and send back
                    self.clients += 1
                    #send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)
                    hostAddr,hostPort=address
                    listenMessage=ServerHostListenMessage(listenInfo=hostPort+1,numPorts=NUMSETS+1)
                    
                    for i in range (1,NUMSETS+2):
                      self.interestingPorts.append(hostPort+i)
                
                    print str(NUMSETS+1)
                    print "Sending listen message to client"
                    send(client,listenMessage)
                    print "Sent listen message to client"

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
                                print str(s)+': '+str(self.dataSetMap[s].myElements)
                                print "Splitting set "+str(s)
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
                                    print "Sending off set " + str(self.dataSetMap[s].myName)
                                    tempset=DataSet(name=self.dataSetMap[s].myName,init=False,size=ELEMENTSPERHOST,elements=builtSets[setnum])
                                    toSend=ServerRegisterDataSet(name=tempset.myName,elementSet=tempset)
                                    print "Sending off set w/elements named" +str(tempset.myElements[tempset.myElements.keys()[0]][0])
                                    time.sleep(0.5)
                                    print self.clientmap[self.clientmap.keys()[setnum]]
                                    send(self.clientmap.keys()[setnum],toSend)
                            #END DISTRIBUTE DATASETS
                            #DISTRIBUTE PROBABILITY DISTRIBUTIONS
                            for c in self.clientmap.keys():
                                probDist={}
                                sum=0
                                for s in self.dataSetMap.keys():
                                    weight=random.random()
                                    probDist[s]=weight
                                    sum+=weight
                                for s in self.dataSetMap.keys():
                                    probDist[s]=probDist[s]/sum
                                toSend=ServerProbabilityUpdateMessage(probId=0,distribution=probDist)
                                send(c,toSend)
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
                                time.sleep(1)
                                send(toClient,ServerSayGoMessage())
                                print "Sent say go"

                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    for toClient in self.clientmap.keys():
                      send(toClient,ServerSayGoMessage())
                else:
                    # handle all other sockets
                    try:
                        # data = s.recv(BUFSIZ)
                        data = receive(s)
                        if data:
                        # Send as new client's message...
                            msg = '\n#[' + self.getname(s) + ']>> ' + data
                            # Send data to all except ourselves
                            for o in self.outputs:
                                if o != s:
                                    temp=1 #this is a pass
                                    # o.send(msg)
                                    #send(o, msg)
                        else:
                            print 'chatserver: %d hung up' % s.fileno()
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)

                            # Send client leaving information to others
                            msg = '\n(Hung up: Client from %s)' % self.getname(s)
                            for o in self.outputs:
                                temp=1 #this is a pass
                                # o.send(msg)
                                #send(o, msg)

                    except socket.error, e:
                        # Remove
                        inputs.remove(s)
                        self.outputs.remove(s)



        self.server.close()

if __name__ == "__main__":
    MMP().serve()
