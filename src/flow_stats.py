#!/usr/bin/python
# Copyright 2012 William Yu
# wyu@ateneo.edu
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX. If not, see <http://www.gnu.org/licenses/>.
#

"""
This is a demonstration file created to show how to obtain flow 
and port statistics from OpenFlow 1.0-enabled switches. The flow
statistics handler contains a summary of web-only traffic.
"""

# standard includes
from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.util import str_to_bool
import StatPacket as sp
import pox.openflow.libopenflow_01 as of
import socket
import sys
import pickle
marshall = pickle.dumps
unmarshall = pickle.loads

# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()

HOST = '192.168.1.124'
PORT = 50009              
hasMMP=False
s = None
def openSocket():
  problem=True
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #s.setblocking(0)
    s.settimeout(1)
  except socket.error as msg:
    s = None
    problem=False
    print 'controller could not set up MMP socket'
  try:
    print 'CONNECTING'
    s.connect((HOST,PORT))
    print 'connecTED'
  except socket.error as msg:
    problem=False
    s.close()
    s = None
    print 'controller could not connect to MMP'
  #s.sendall('Controller is up')
  if s is None:
    print 'could not open socket'
    problem=False
    #sys.exit(1)
  return (s,problem)
  #for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
  #                            socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
  #  af, socktype, proto, canonname, sa = res
  #  try:
  #    s = socket.socket(af, socktype, proto)
  #    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  #  except socket.error as msg:
  #    s = None
  #    continue
  #  try:
  #    s.bind(sa)
  #    s.listen(1)
  #  except socket.error as msg:
  #    s.close()
  #    s = None
  #    continue
  #  break
  #if s is None:
  #  print 'could not open socket'
  #  sys.exit(1)
  #conn, addr = s.accept()
  #print 'Connected by', addr
  #return (conn, addr, s)

def closeSocket(s, conn):
  conn.close()
  s.close()

def sendRecvMMP(s, flow_data):
  #while 1:
    #incoming_data = s.recv(1024)
    #if not incoming_data: continue 
    #else: 
  global hasMMP
  print hasMMP
  try:
    if(s is not None):
      print 'Hey I\'m sending stuff to the MMP'
      s.send('ERROR' if not flow_data else flow_data)
    else:
      print 'reconnecting...'
      (s,hasMMP)=openSocket()
      #import pdb; pdb.set_trace()
  except socket.error as e:
    print "Socket error"
    #break
  return s

# handler for timer function that sends the requests to all the
# switches connected to the controller.
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
  #log.debug("FlowStatsReceived from %s: %s", 
  #  dpidToStr(event.connection.dpid), stats)

  # Get number of bytes/packets in flows for web traffic only
  w_bytes = 0
  w_flows = 0
  w_packet = 0
  for f in event.stats:
      print f.match.nw_src, f.match.tp_src, f.match.nw_dst, f.match.tp_dst, f.match.dl_dst
      w_bytes += f.byte_count
      w_packet += f.packet_count
      w_flows += 1
  #log.info("Web traffic from %s: %s bytes (%s packets) over %s flows", 
  #  dpidToStr(event.connection.dpid), w_bytes, w_packet, w_flows)

  flow_packet_whole = sp.FlowStatPacket(w_bytes, w_packet, w_flows, stats)
  flow_packet = flow_packet_whole.getPacket();
#  flow_packet.printData()
  flow_stat_data = marshall(flow_packet)
  global sock
  sock = sendRecvMMP(sock, flow_stat_data)

# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("PortStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)

  port_packet = sp.PortStatPacket(stats)
  #port_packet.printData()
  port_stat_data = marshall(port_packet)
  global sock
  sock = sendRecvMMP(sock, port_stat_data)


class TestSwitch(EventMixin):
  def __init__(self, connection):
    self.connection = connection
    self.listenTo(connection)
    self.macToPort = {}
    
  def _handle_PacketIn(self, event):
  
    def flood(message = None):
      if message is not None: log.debug(message)
      msg = of.ofp_packet_out()
      msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      msg.buffer_id = event.ofp.buffer_id
      msg.in_port = event.port
      self.connection.send(msg)
  
    packet = event.parse()
  
    self.macToPort[packet.src] = event.port 
    #log.debug("Incoming: %s.%s, Destination: %s" % 
    #           (packet.src,event.port,packet.dst))
  
    # Install flow table entry in the switch so this flow goes
    # out the appropriate port
    if packet.dst not in self.macToPort:
      flood("Port for %s unknown -- flooding" % (packet.dst,))
    else:
      port = self.macToPort[packet.dst]
  
      #log.debug("installing flow for %s.%i -> %s.%i" %
      #           (packet.src, event.port, packet.dst, port))
      #log.debug("number of flows: " + str(len(self.macToPort))) 
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet, event.port)
      msg.idle_timeout = 5
      msg.hard_timeout = 10
      msg.actions.append(of.ofp_action_output(port = port))
      msg.data = event.ofp
      self.connection.send(msg)

class Test(EventMixin):
  def __init__(self):
    self.listenTo(core.openflow)

  def _handle_ConnectionUp(self, event):
    TestSwitch(event.connection)


#import pdb; pdb.set_trace()
(sock,hasMMP) = openSocket()

# main functiont to launch the module
def launch ():
  from pox.lib.recoco import Timer
  # attach handsers to listners
  core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 
  #core.openflow.addListenerByName("PortStatsReceived", 
  #  _handle_portstats_received) 
  core.registerNew(Test)

  # timer set to execute every five seconds
  Timer(5, _timer_func, recurring=True)
