# Echo client program
import socket
import sys
import time

HOST = 'localhost'    # The remote host
PORT = 50008              # The same port as used by the server
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
  af, socktype, proto, canonname, sa = res
  try:
    s = socket.socket(af, socktype, proto)
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

while True:
  s.sendall('MMP is alive')
  data = s.recv(1024)
  if data:
    print 'Received', repr(data)
  else:
    print 'no data'
  time.sleep(1)
  data = None
s.close()
