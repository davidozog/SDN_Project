#Attribution: http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
import socket
import sys
import select
from communication import *
import pdb

BUFSIZ = 1024
READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
class ChatClient(object):
    """ A simple command line chat client using select """

    def __init__(self, name, host='127.0.0.1', port=3490):
    	self.myDataSets = {}
	self.myProbabilities = {}
        self.name = name
        # Quit flag
        self.hostsmap={}
	self.dataSetMap={}
        self.flag = False
        self.port = int(port)
        self.host = host
        # Initial prompt
	self.fdmap={}
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
            print 'Could not connect to chat server @%d' % self.port
            sys.exit(1)

    def cmdloop(self):
        numRcvd=0
        while not self.flag:
            try:
                sys.stdout.flush()
		inputs = [self.sock]
                # Wait for input from stdin & socket
                #inputready, outputready,exceptrdy = select.poll(inputs, [],[])
		inputready=[]
		inputready= self.poller.poll(1000) #wait 1 second
                for ifd,evtype in inputready:	
		    if not (evtype & (select.POLLIN | select.POLLPRI)):
		    	continue
		    i=self.fdmap[ifd]
                    print "IFD= "+str(ifd)
                    if i == self.sock:
			print "IFD IS OF SOCK"
                        data = receive(self.sock)
                        if not data:
                            print 'Shutting down.'
                            self.flag = True
                            break
                        else:
			    if isinstance(data,ServerHostAlertMessage):
				try:
					data=data.myHostInfo
					newsocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					haddr,hport=data
					print "Sending on "+str(hport)
					newsocket.connect(data)
					self.hostsmap[data]=newsocket   
					tmsg=ClientSayEhlo()
					send(newsocket,tmsg)
					self.fdmap[newsocket.fileno()]=newsocket
					self.poller.register(newsocket,READ_ONLY)
        			except socket.error, e:
			            print 'Could not connect to chat server @%d' % self.port
			    elif isinstance(data,ServerHostListenMessage):

				listenport=data.myListenInfo
        			self.listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			        self.listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			        self.listensocket.bind(('',listenport))
				print ("Listening on port "+str(listenport))
				self.listensocket.listen(5)
				inputs.append(self.listensocket)
				self.poller.register(self.listensocket,READ_ONLY)
				self.fdmap[self.listensocket.fileno()]=self.listensocket
			    elif isinstance(data,ServerRegisterDataSet):
				numRcvd+=1
				ds=data.myElements
			        self.dataSetMap[ds.myName]=ds	
			    else:
	                        pdb.set_trace()
		    elif i ==self.listensocket:
			print "IFD is of LISTENSOCKET"
		    	client,address =self.listensocket.accept()
			print "Received Client to Client Message"
			print "Length of set 0: "+str(len(self.dataSetMap[0].myElements.keys()))
			print "Length of set 1: "+str(len(self.dataSetMap[1].myElements.keys()))
			pdb.set_trace()
		    else:
			print "Data from unexpected source"
            except KeyboardInterrupt:
                print 'Interrupted.'
                self.sock.close()
                break
            
            
if __name__ == "__main__":
    import sys

    if len(sys.argv)<3:
        sys.exit('Usage: %s chatid host portno' % sys.argv[0])
        
    client = ChatClient(sys.argv[1],sys.argv[2], int(sys.argv[3]))
    client.cmdloop()
