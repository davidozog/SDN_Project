class StatPacket():
  
  def __init__(self, stats=[]):
    self.stats = stats
    self.num_stats = len(stats)

  def printData(self):

    print "\n******************************************************************"
    print "                    " + self.packet_type + " # " + self.ID + "     "
    print "******************************************************************"

    for i in range( self.num_stats ):
      print "\n Statistic #" + str(i)
      for k,v in self.stats[i].iteritems():
        print "   " + k + " : " + str(v)+ "\n"
  


class PortStatPacket(StatPacket):

  global pmeasurement_id 
  pmeasurement_id = 0

  def __init__(self, stats=[]):

    StatPacket.__init__(self, stats)

    self.packet_type = "Port Statistics"

    # stats keys and example values:
    #   'rx_over_err' : 0
    #   'tx_dropped' : 0
    #   'rx_packets' : 5
    #   'rx_frame_err' : 0
    #   'rx_bytes' : 378
    #   'tx_errors' : 0
    #   'rx_crc_err' : 0
    #   'collisions' : 0
    #   'rx_errors' : 0
    #   'tx_bytes' : 854
    #   'rx_dropped' : 0
    #   'tx_packets' : 15
    #   'port_no' : 3

    global pmeasurement_id
    pmeasurement_id += 1
    self.ID = str(pmeasurement_id)


class FlowStatPacket(StatPacket):

  global measurement_id 
  measurement_id = 0

  def __init__(self, fbytes=-1, pcount=-1, fcount=-1, stats=[]):
    
    StatPacket.__init__(self, stats)

    self.packet_type = "Flow Statistics"

    # stats keys and example values:
    #   'packet_count' : 1
    #   'hard_timeout' : 30
    #   'byte_count' : 42
    #   'duration_sec' : 2
    #   'actions' : [{'max_len': 0, 'type': 'OFPAT_OUTPUT', 'port': 2}] 
    #   'duration_nsec' : 870000000
    #   'priority' : 65535 
    #   'idle_timeout' : 10
    #   'cookie' : 0
    #   'table_id' : 0
    #   'match' ... 
    #       This is an example of a match dictionary:
    #           'dl_type': 'IP', 
    #           'in_port': 2}
    #           'nw_dst': IPAddr('10.0.0.1'), 
    #           'nw_src': IPAddr('10.0.0.2'), 
    #           'dl_src': '00:00:00:00:00:02', 
    #           'dl_dst': '00:00:00:00:00:01', 
    #           'dl_vlan': 65535, 
    #           'dl_vlan_pcp': 0, 
    #           'get_nw_src': '10.0.0.2/32', 
    #           'get_nw_dst': '10.0.0.1/32', 
    #           'tp_src': 0, 
    #           'tp_dst': 0, 
    #           'nw_proto': 1, 
    #           'nw_tos': 0, 

    global measurement_id
    measurement_id += 1
    self.ID = str(measurement_id)

  def getPacket(self):
    tpsrc = []
    bytemap={}
    if (self.num_stats==0):
      return "None"
    for p in range(0,self.num_stats):
      filterStr='dst' 
      tp = 'tp_' + filterStr
      nw = 'nw_' + 'src'
      if self.stats[p]['match'].has_key(tp):
        index=(self.stats[p]['match'][nw],self.stats[p]['match'][tp])
        if bytemap.has_key(self.stats[p]['match'][tp]):
          bytemap[index]=bytemap[index]+self.stats[p]['byte_count']
        else:
          bytemap[index]=self.stats[p]['byte_count']
    print bytemap
    return bytemap
