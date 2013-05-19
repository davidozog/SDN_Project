#Attribution: http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
import socket
import sys
import select
from communication import *
import pdb

BUFSIZ = 1024

class ChatClient(object):
    """ A simple command line chat client using select """

    def __init__(self, name, host='127.0.0.1', port=3490):
        self.name = name
        # Quit flag
        self.hostsmap={}
        self.flag = False
        self.port = int(port)
        self.host = host
        # Initial prompt
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
	    self.prompt="Puppy?"
        except socket.error, e:
            print 'Could not connect to chat server @%d' % self.port
            sys.exit(1)

    def cmdloop(self):

        while not self.flag:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin & socket
                inputready, outputready,exceptrdy = select.select([0, self.sock], [],[])
                
                for i in inputready:
                    if i == 0:
                        data = sys.stdin.readline().strip()
                        if data: send(self.sock, data)
			
		
                    elif i == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print 'Shutting down.'
                            self.flag = True
                            break
                        else:
			    if isinstance(data,ServerHostAlertMessage):
				data=data.myHostInfo
				newsocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				newsocket.connect(data)
				self.hostsmap[data]=newsocket   
			    elif isinstance(data,ServerHostListenMessage):
				listenport=data.myListenInfo
        			self.listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			        self.listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			        self.listensocket.bind(('',listenport))
				self.listensocket.listen(16)
				
			    else:
	                        pdb.set_trace()
		    elif i ==self.listensocket:
		    	client,address =self.listensocket.accept()
			pdb.set_trace()
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
