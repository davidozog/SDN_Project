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
#READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_ONLY = select.POLLIN | select.POLLPRI
class ChatClient(object):
    """ A simple command line chat client using select """

    def __init__(self, name, host='127.0.0.1', port=3490):
        self.myProbabilityMap = {}
        self.myReturnProbabilities = {}
        self.name = name
        # Quit flag
        self.hostsmap={}
        self.dataSetMap={}
        self.flag = False
        self.port = int(port)
        self.host = host
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
            #apeprint 'Connected to chat server@%d' % self.port
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
            #apeprint 'Could not connect to chat server @%d' % self.port
            sys.exit(1)
    def chooseSet(self,distribution):
        r = random.random()
        sum = distribution[distribution.keys()[0]]
        i = 1
        while(r>sum):
            sum+=distribution[distribution.keys()[i]]
            i+=1
        i-=1
        return distribution.keys()[i]
    def chooseReturn(self,distribution,element):
        others=0
        numothers=0
        val=distribution[element]
        for key in distribution.keys():
          if(key!=element):
            others+=distribution[key]
            numothers+=1
        temp=val/(others/numothers) if others!= 0 else 0
        return (1-math.pow(2,-temp))

    def chooseElement(self, setName):
        r = random.random()
        idx = self.dataSetMap[setName].numElements() * r
        return int(idx)
    def cmdloop(self):
        numRcvd=0
        phase=0
        idle=0
        passNum=0
        while not self.flag:
            try:
                if(passNum%200==2):
                  print 'At pass '+str(passNum)+' I received '+str(numRcvd)+' elements (cumulatively)'
                  for key in self.dataSetMap.keys():
                    print 'In dataset '+str(key)+':'+str(len(self.dataSetMap[key].myElements.keys()))
                sys.stdout.flush()
                inputs = [self.sock]
                # Wait for input from stdin & socket
                #inputready, outputready,exceptrdy = select.poll(inputs, [],[])
                inputready=[]
                inputready= self.poller.poll(10)
                ##apeprint "Foofoofoo???"
                idle+=1
                if(phase==1) and (self.gotMyElement):

                    choiceSet=self.chooseSet(self.myProbabilityMap)
                    mySet=self.dataSetMap[choiceSet].myName
                    choiceElement=self.chooseElement(mySet)
                    passNum+=1

                    if(not self.dataSetMap[choiceSet].myElements.has_key(choiceElement)):
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
                            time.sleep(0.001)
                            tkey[-1].connect(peer)
                            #apeprint(tkey[-1].fileno())
                            #hostmap[key][-1].close()
                            send(self.hostsmap[key][-1],request)
                            #apeprint "Sent off "+str(request)+" to "+str(tkey[-1].getpeername())

                for ifd,evtype in inputready:
                    if not (evtype & (select.POLLIN | select.POLLPRI)):
                        continue
                    #apeprint "I received any data"
                    idle=0
                    i=self.fdmap[ifd]
                    #apeprint "IFD= "+str(ifd)
                    if(phase%2==0) and (phase>0):
                      pdb.set_trace()
                    if i == self.sock:
                        #apeprint "IFD IS OF SOCK"
                        #tempsock,toss = self.sock.accept()
                        data = receive(self.sock)
                        #apeprint data
                        if not data:
                            #apeprint 'Shutting down.'
                            self.flag = True
                            break
                        else:
                            if isinstance(data,ServerHostAlertMessage):
                                self.sendSockets={}
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
                                    #apeprint 'Could not connect to chat server @%d' % self.tport
                                    print '======================='
                                    #pdb.set_trace()
                            elif isinstance(data,ServerHostListenMessage):
                                listenport=data.myListenInfo

                                self.numSets=data.myNumPorts
                                self.myListeners=[]
                                for channel in range(self.numSets):
                                    #apeprint "Listening on "+str(listenport+channel)

                                    listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                                    listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                            elif isinstance(data,ServerRegisterDataSet):
                                #numRcvd+=1
                                #apeprint "modified my data map"
                                ds=data.myElements
                                self.dataSetMap[ds.myName]=ds
                            elif isinstance(data,ServerProbabilityUpdateMessage):
                                self.myProbabilityMap=data.myDistribution
                            elif isinstance(data,ServerSayGoMessage):
                                phase=1
                                time.sleep(1)
                            #elif isinstance(
                            else:
                                #apeprint "Unknown packet type from server"
                                pdb.set_trace()

                    elif i==self.controlChannel:
                        #apeprint "Foo?"
                        #if not self.ephemeralSockets.has_key(i):
                        #  self.ephemeralSockets[i]=hostSock
                        hostSock,toss=i.accept()
                        addr,prt=toss
                        #else:
                        #  hostSock=self.ephemeralSockets[i]
                        data = receive(hostSock)
                        #apeprint data
                        #apeprint "Moo?"
                        if isinstance(data,ClientRequestDataMessage):
                            dataset=data.myDataSet
                            element=data.myElement
                            response=ClientResponseMessage()
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
                            self.fdmap[self.sendSockets[addr][dataset].fileno()]=self.sendSockets[addr][dataset]
                            send(self.sendSockets[addr][dataset],response)
                            
                            #apeprint "Done???!?!!!"
                        #hostSock.close()
                    elif i in self.myListeners: #listensocket
                        hostSock, toss = i.accept()
                        addr,toss2=toss
                        #apeprint "Received packet from other host"
                        #pdb.set_trace()
                        thing3=0
                        data = receive(hostSock)
                        if isinstance(data,ClientResponseMessage) and data.myElement!=None:
                          setname,element,value=data.myElement
                          dataset=setname
                          self.gotMyElement=True
                          numRcvd+=1
                          print "Receiving totally lemitigate data "+str(data.myElement)
                          if(data.myKeepable):
                            toKeep=self.chooseReturn(self.myProbabilityMap,setname)
                            if(random.random()>toKeep):
                              self.dataSetMap[dataset].myElements[element]=data.myElement
                              bestEffort=0
                              rset=dataset
                              numSets=len(self.dataSetMap.keys())
                              mySet=""
                              while(rset==dataset) and (bestEffort<1000):
                                rset=self.dataSetMap[choiceSet].myName
                                temp=int(random.random()*numSets)
                                choiceSet=self.dataSetMap.keys()[temp]
                                bestEffort+=1
                              rElement=-1 if rset!=dataset else self.dataSetMap[rset].myElements[self.dataSetMap[rset].myElements.keys()[0] ]
                              while (bestEffort<1000) and (not self.dataSetMap[rset].myElements.has_key(rElement)):
                                rElement=self.chooseElement(self.dataSetMap[rset].myName)
                                bestEffort+=1 
                              replacementElement=self.dataSetMap[rset].myElements[rElement] 
                              #apeprint "Requesting deletion of "+str(dataset)+", element "+str(element)
                              request=ClientRequestDeletion(dataSet=data.myDataSet,element=element,replacement=replacementElement)
                              self.sendSockets[addr][dataset].close()
                              self.sendSockets[addr][dataset]= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                              taddr,tprt=self.numToBase[addr]
                              self.sendSockets[addr][dataset].connect((addr,tprt+dataset))
                              self.fdmap[self.sendSockets[addr][dataset].fileno()]=self.sendSockets[addr][dataset]
                              send(self.sendSockets[addr][dataset],request)
                              del self.dataSetMap[rset].myElements[rElement]
                          print 'Done receiving data'
                        if isinstance(data,ClientRequestDeletion):
                          
                          print "Received delete request"
                          dataset=data.myDataSet
                          element=data.myElement
                          if(self.dataSetMap[dataset].myElements.has_key(element)):
                              del self.dataSetMap[dataset].myElements[element]
                              replacement=data.myReplacement
                              name,junk,stuff=replacement
                              if(self.dataSetMap[name].myElements.has_key(junk)):
                                print "Error in replacement, received duplicate"
                                pdb.set_trace()
                              else:
                                self.dataSetMap[name].myElements[junk]=replacement
                          else:
                              print "Warning: received request to delete nonexistent element"
                              pdb.set_trace()
                          print 'Finished dealing with delete request'+str(dataset)+','+str(element)
                        #hostSock.close()
                    #elif i==self.controlChannel:
                #       i.accept()
                 #       data = receive(self.controlChannel)
                    else:
                        #pdb.set_trace()
                        toss=0
                        print "Data from unexpected source"
            except KeyboardInterrupt:
                #apeprint 'Interrupted.'
                self.sock.close()
                break
            except socket.error, e:
                #apeprint "Socket error"
                tb=traceback.format_exc()
                #apeprint tb
                pdb.set_trace()

if __name__ == "__main__":
    import sys

    if len(sys.argv)<3:
        sys.exit('Usage: %s chatid host portno' % sys.argv[0])

    client = ChatClient(sys.argv[1],sys.argv[2], int(sys.argv[3]))
    client.cmdloop()
