# Echo client program
import socket
import sys
import time
import os

HOST = 'localhost'    # The remote host
myPort=sys.argv[-1]   # The same port as used by the server
otherPort=sys.argv[-2]
time.sleep(1)

listenersocket=scoket.socket(socket.AF_INET,socket.SOCK_STREAM)
listenersocket.bind((socket.gethostname(),myPort))
listenersocket.listen(16)
