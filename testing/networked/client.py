#Attribution: http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/

import socket
import sys
import select
from communication import *
import pdb
import random
BUFSIZ = 1024
#READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_ONLY = select.POLLIN | select.POLLPRI
class ChatClient(object):
    """ A simple command line chat client using select """

    def __init__(self, name, host='127.0.0.1', port=3490):
        self.myProbabilityMap = {}
        self.name = name
        # Quit flag
        self.hostsmap={}
        self.dataSetMap={}
        self.flag = False
        self.port = int(port)
        self.host = host
        self.iterations = 0
	
        self.gotMyElement=True;
        # Initial prompt
        self.fdmap={}
        self.numToBase={} 
	self.prompt='[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print 'Connected to chat server@%d' % self.port
            # Send my name..
            send(self.sock,ClientSayEhlo())
            #send(self.sock,'NAME: ' + self.name)
            # Contains client address, set it
            self.prompt="Puppy? "
            self.fdmap[self.sock.fileno()]=self.sock
            self.poller=select.poll()
            self.poller.register(self.sock,READ_ONLY)
            print "SOCK FD "+str(self.sock.fileno())
        except socket.error, e:
            print 'problem at 1'
            print 'Could not connect to chat server @%d' % self.port
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

    def chooseElement(self, setName):
        r = random.random()
        idx = self.dataSetMap[setName].numElements() * r
        return int(idx)
    def cmdloop(self):
        numRcvd=0
        phase=0
        idle=0

        while not self.flag:
            try:
                sys.stdout.flush()
                inputs = [self.sock]
                # Wait for input from stdin & socket
                #inputready, outputready,exceptrdy = select.poll(inputs, [],[])
                inputready=[]
                inputready= self.poller.poll(1000)
                print "Foofoofoo???"
                idle+=1
                if(phase==1) and (self.gotMyElement):

                    choiceSet=self.chooseSet(self.myProbabilityMap)
                    mySet=self.dataSetMap[choiceSet].myName
                    choiceElement=self.chooseElement(mySet)
                    if(not self.dataSetMap[choiceSet].myElements.has_key(choiceElement)):
                        request=ClientRequestDataMessage(dataSet=choiceSet,element=choiceElement)
                        self.gotMyElement=False
                        for key in self.hostsmap.keys():
			    print "Sending"
                            tkey=self.hostsmap[key]
		            peer=tkey[-1].getpeername()
			    tkey[-1].close()
                            tkey[-1]= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			    tkey[-1].connect(peer)
                            #hostmap[key][-1].close()
                            send(tkey[-1],request)
                            print "Sent off "+str(request)+" to "+str(tkey[-1].getpeername())
 
                for ifd,evtype in inputready:
                    if not (evtype & (select.POLLIN | select.POLLPRI)):
                        continue
                    print "I received any data"
                    idle=0
                    i=self.fdmap[ifd]
                    print "IFD= "+str(ifd)
                    if i == self.sock:
                        print "IFD IS OF SOCK"
			tempsock,toss = self.sock.accept
                        data = receive(tempsock)
                        print data
                        if not data:
                            print 'Shutting down.'
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
                                        #newsocket.setblocking(0)
                                        self.tport=hport+i
                                        print "Sending on "+str(hport+i)
                                        newsocket.connect((haddr,hport+i))
                                        numRcvd=1
                                        print newsocket
                                        tmsg=ClientSayEhlo()
                                        send(newsocket,tmsg)
                                        self.fdmap[newsocket.fileno()]=newsocket
                                        #self.poller.register(newsocket,READ_ONLY)
                                        self.sendSockets[(haddr)][i if i!=(self.numSets-1) else -1]=newsocket
                                        if(not self.hostsmap.has_key(hostName)):
                                            self.hostsmap[hostName]={}
                                        self.hostsmap[hostName][i if i!=(self.numSets-1) else -1]=newsocket
					
                                except socket.error, e:
                                    print 'problem at 2'
                                    print 'Could not connect to chat server @%d' % self.tport
                                    print '======================='
                                    #pdb.set_trace()
                            elif isinstance(data,ServerHostListenMessage):
                                listenport=data.myListenInfo

                                self.numSets=data.myNumPorts
                                self.myListeners=[]
                                for channel in range(self.numSets):
                                    print "Listening on "+str(listenport+channel)

                                    listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    listensocket.setblocking(0)
                                    listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                    print listensocket
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
                                ds=data.myElements
                                self.dataSetMap[ds.myName]=ds
                            elif isinstance(data,ServerProbabilityUpdateMessage):
                                self.myProbabilityMap=data.myDistribution
                            elif isinstance(data,ServerSayGoMessage):
                                phase=1
                                import time
                                time.sleep(1)
                            #elif isinstance(
                            else:
				print "Unknown packet type from server"
                                pdb.set_trace()

                    elif i==self.controlChannel:
                        print "Foo?"
                        #if not self.ephemeralSockets.has_key(i):
                        #  self.ephemeralSockets[i]=hostSock
                        hostSock,toss=i.accept()
                        addr,prt=toss
                        #else:
                        #  hostSock=self.ephemeralSockets[i]
                        data = receive(hostSock)
                        print data
                        print "Moo?"
                        if isinstance(data,ClientRequestDataMessage):
                          dataset=data.myDataSet
                          element=data.myElement
			  response=ClientResponseMessage()
			  if(self.dataSetMap[dataset].myElements.has_key(element)):
				response.myKeepable=self.dataSetMap[dataset].checkRequests(element)
				response.myElement=self.dataSetMap[dataset].myElements[element]
			        response.myDataSet=self.dataSetMap[dataset].myName
			  #pdb.set_trace()
                          sockToSend=self.sendSocket[addr][dataset] #UNSAFE FOR SINGLE HOST
			  
			  send(hostSock,response)	
			  print "Done???!?!!!"  
#                        #pdb.set_trace()

                    elif i in self.myListeners: #listensocket
			hostSock, toss = i.accept()
#                       #pdb.set_trace()
                        print "Received packet from other host"
                        print "Received packet from other host"
                        print "Received packet from other host"

                        thing3=0
                        data = receive(hostSock)
                        print "wat"
                    #elif i==self.controlChannel:
                #       i.accept()
                #       print "Foo?"
                 #       data = receive(self.controlChannel)
                    else:
                        #pdb.set_trace()
                        print "Data from unexpected source"
            except KeyboardInterrupt:
                print 'Interrupted.'
                self.sock.close()
                break
	    except socket.error, e:
		print "Socket error"
		#pdb.set_trace()

if __name__ == "__main__":
    import sys

    if len(sys.argv)<3:
        sys.exit('Usage: %s chatid host portno' % sys.argv[0])

    client = ChatClient(sys.argv[1],sys.argv[2], int(sys.argv[3]))
    client.cmdloop()
