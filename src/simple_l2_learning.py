from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.util import str_to_bool
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

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

def launch(transparent=False):
  core.registerNew(Test)
