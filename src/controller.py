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
import socket
import sys
from pox.core import core
from pox.lib.util import dpidToStr
from pox.lib.util import str_to_bool
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.revent import *
from pox.openflow.of_json import *

log = core.getLogger()

HOST = 'localhost'        
PORT = 50008              

def openSocket():
  s = None
  for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
      s = socket.socket(af, socktype, proto)
    except socket.error as msg:
      s = None
      continue
    try:
      s.bind(sa)
      s.listen(1)
    except socket.error as msg:
      s.close()
      s = None
      continue
    break
  if s is None:
    print 'could not open socket'
    sys.exit(1)
  conn, addr = s.accept()
  print 'Connected by', addr
  return (conn, addr, s)

def closeSocket(s, conn):
  conn.close()
  s.close()

def sendRecvMMP(s, conn):
  while 1:
    data = conn.recv(1024)
    if not data: continue 
    else: 
      conn.send(data)
      break

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
  log.debug("FlowStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)

  # Get number of bytes/packets in flows for web traffic only
  web_bytes = 0
  web_flows = 0
  web_packet = 0
  for f in event.stats:
    if f.match.tp_dst == 80 or f.match.tp_src == 80:
      web_bytes += f.byte_count
      web_packet += f.packet_count
      web_flows += 1
  log.info("Web traffic from %s: %s bytes (%s packets) over %s flows", 
    dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)

  sendRecvMMP(sock, conn)
  #closeSocket(sock, conn)

# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("PortStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)
    

(conn, add, sock) = openSocket()

# main functiont to launch the module


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
    log.debug("Incoming: %s.%s, Destination: %s" % 
               (packet.src,event.port,packet.dst))

    # Install flow table entry in the switch so this flow goes
    # out the appropriate port
    if packet.dst not in self.macToPort:
      flood("Port for %s unknown -- flooding" % (packet.dst,))
    else:
      port = self.macToPort[packet.dst]

      log.debug("installing flow for %s.%i -> %s.%i" %
                 (packet.src, event.port, packet.dst, port))
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet, event.port)
      msg.idle_timeout = 10
      msg.hard_timeout = 30
      msg.actions.append(of.ofp_action_output(port = port))
      msg.data = event.ofp
      self.connection.send(msg)


class Test(EventMixin):
  def __init__(self):
    self.listenTo(core.openflow)

  def _handle_ConnectionUp(self, event):
    TestSwitch(event.connection)
def launch ():
  from pox.lib.recoco import Timer
  core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 
  core.openflow.addListenerByName("PortStatsReceived", 
    _handle_portstats_received) 
  Timer(5, _timer_func, recurring=True)
  core.registerNew(Test)
