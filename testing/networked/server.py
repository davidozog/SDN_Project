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
BUFSIZ = 1024
NUMCLIENTS=2
NUMSETS=2
ELEMENTSPERSET=100
assert (NUMSETS*ELEMENTSPERSET)%NUMCLIENTS==0
ELEMENTSPERHOST=(NUMSETS*ELEMENTSPERSET)/NUMCLIENTS
class ChatServer(object):
    """ Simple chat server using select """
    
    def __init__(self, port=3490, backlog=5):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print 'Listening to port',port,'...'
        self.server.listen(backlog)
        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
        self.distributionMap={}
        self.dataSetMap={}
	for i in range(NUMSETS):
		name=i
		self.dataSetMap[name]=DataSet(name=name,init=True,size=ELEMENTSPERSET)

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
    def serve(self):
        
        inputs = [self.server,sys.stdin]
        self.outputs = []

        running = 1
	phase=0
        while running:

            try:
                inputready,outputready,exceptready = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            except socket.error, e:
                break

            for s in inputready:

                if s == self.server:
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
		    listenMessage=ServerHostListenMessage(listenInfo=hostPort+1)
		    send(client,listenMessage)
		    if(self.clients==NUMCLIENTS):
	                    if(phase==0):
				numFree=[]
				for c in range(NUMCLIENTS):
					numFree.append(ELEMENTSPERHOST)
				for s in range(NUMSETS):
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
					for set in range(NUMCLIENTS):
						tempset=DataSet(name=self.dataSetMap[s].myName,init=False,size=ELEMENTSPERHOST,elements=builtSets[set])
						toSend=ServerRegisterDataSet(name=tempset.myName,elementSet=tempset)
						print "Sending off set named" +str(tempset.myName)
						print self.clientmap[self.clientmap.keys()[set]]
						send(self.clientmap.keys()[set],toSend)	
				phase=1
				for fromClient in self.clientmap.keys():
					for toClient in self.clientmap.keys():
						if fromClient!=toClient:
							details,toss=self.clientmap[fromClient]
							addr,prt=details
							prt+=1
							details=(addr,prt)
							sendme=ServerHostAlertMessage(hostInfo=details)
							send(toClient,sendme)
			    			            
                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0
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
    ChatServer().serve()
