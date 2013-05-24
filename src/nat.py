#!/usr/bin/python
 
"""
Example to create a Mininet topology and connect it to the internet via NAT
through eth0 on the host.
 
Glen Gibb, February 2011
 
(slight modifications by BL, 5/13)
"""
 
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.node import Node, RemoteController
from mininet.topolib import TreeNet
from mininet.topo import Topo
 
#################################
def startNAT( root, inetIntf='eth0', subnet='10.0/8' ):
    """Start NAT/forwarding between Mininet and external network
    root: node to access iptables from
    inetIntf: interface for internet access
    subnet: Mininet subnet (default 10.0/8)"""
 
    # Identify the interface connecting to the mininet network
    localIntf =  root.defaultIntf()
 
    # Flush any currently active rules
    root.cmd( 'iptables -F' )
    root.cmd( 'iptables -t nat -F' )
 
    # Create default entries for unmatched traffic
    root.cmd( 'iptables -P INPUT ACCEPT' )
    root.cmd( 'iptables -P OUTPUT ACCEPT' )
    root.cmd( 'iptables -P FORWARD DROP' )
 
    # Configure NAT
    root.cmd( 'iptables -I FORWARD -i', localIntf, '-d', subnet, '-j DROP' )
    root.cmd( 'iptables -A FORWARD -i', localIntf, '-s', subnet, '-j ACCEPT' )
    root.cmd( 'iptables -A FORWARD -i', inetIntf, '-d', subnet, '-j ACCEPT' )
    root.cmd( 'iptables -t nat -A POSTROUTING -o ', inetIntf, '-j MASQUERADE' )
 
    # Instruct the kernel to perform forwarding
    root.cmd( 'sysctl net.ipv4.ip_forward=1' )
 
def stopNAT( root ):
    """Stop NAT/forwarding between Mininet and external network"""
    # Flush any currently active rules
    root.cmd( 'iptables -F' )
    root.cmd( 'iptables -t nat -F' )
 
    # Instruct the kernel to stop forwarding
    root.cmd( 'sysctl net.ipv4.ip_forward=0' )
 
    # Restart network-manager
    root.cmd( 'service network-manager start' )
 
def connectToInternet( network, switch='s1', rootip='10.254', subnet='10.0/8'):
    """Connect the network to the internet
       switch: switch to connect to root namespace
       rootip: address for interface in root namespace
       subnet: Mininet subnet"""
    switch = network.get( switch )
    prefixLen = subnet.split( '/' )[ 1 ]
    routes = [ subnet ]  # host networks to route to
 
    # Create a node in root namespace
    root = Node( 'root', inNamespace=False )
 
    # Stop network-manager so it won't interfere
    root.cmd( 'service network-manager stop' )
 
    # Create link between root NS and switch
    link = network.addLink( root, switch )
    link.intf1.setIP( rootip, prefixLen )
 
    # Start network that now includes link to root namespace
    network.start()
 
    # Start NAT and establish forwarding
    startNAT( root )
 
    # Establish routes from end hosts
    for host in network.hosts:
        host.cmd( 'ip route flush root 0/0' )
        host.cmd( 'route add -net', subnet, 'dev', host.defaultIntf() )
        host.cmd( 'route add default gw', rootip )
 
    print "*** Hosts are running and should have internet connectivity"
    print "*** Type 'exit' or control-D to shut down network"
    CLI( network )
 
    stopNAT( root )


class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        leftHost2 = self.addHost( 'h3' )
        rightHost2 = self.addHost( 'h4' )
        leftSwitch = self.addSwitch( 's1' )
        #rightSwitch = self.addSwitch( 's4' )

        # Add links
        self.addLink( leftHost, leftSwitch )
        self.addLink( rightHost, leftSwitch )
        #self.addLink( rightSwitch, rightHost )
        self.addLink( leftHost2, leftSwitch )
        self.addLink( rightHost2, leftSwitch )
        #self.addLink( leftSwitch, rightSwitch )

        self.switch = leftSwitch

    def get( self, switch ):
      return self.switch


 
if __name__ == '__main__':
    lg.setLogLevel( 'info')
    net = TreeNet( depth=1, fanout=4, controller=lambda name: RemoteController( name, ip='127.0.0.1' ) )
    #topos = { 'mytopo': ( lambda: MyTopo() ) }
    #net = MyTopo()
    connectToInternet( net )
    net.stop()
