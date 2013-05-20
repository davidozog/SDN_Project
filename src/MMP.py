#5 Echo client program
import socket
import sys
import time
import pickle
import StatPacket 
marshall = pickle.dumps
unmarshall = pickle.loads

HOST = 'localhost'    # The remote host
PORT = 50008              # The same port as used by the server
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
  af, socktype, proto, canonname, sa = res
  try:
    s = socket.socket(af, socktype, proto)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  except socket.error as msg:
    s = None
    continue
  try:
    s.connect(sa)
  except socket.error as msg:
    s.close()
    s = None
    continue
  break
if s is None:
  print 'could not open socket'
  sys.exit(1)

#flow_stat_data = fsp.FlowStatPacket()

while True:
  s.sendall('MMP is alive')
  data = s.recv(8192)
  #import pdb; pdb.set_trace()
  if data:
    flow_stat_data = unmarshall(data)
    print 'Received:', flow_stat_data.printData()
  else:
    print 'no data'
  time.sleep(1)
  data = None
s.close()
