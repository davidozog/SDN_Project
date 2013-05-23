#http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/

import cPickle
import socket
import struct
import random
marshall = cPickle.dumps
unmarshall = cPickle.loads
DATASIZE_PER_HOST=100
REQUESTS_CACHED=10
class DataSet:
    def __init__(self,name="None Given",init=True,size=DATASIZE_PER_HOST,elements={}):
        self.myName = name
        self.myElements=elements
        self.pastRequests=[]
        if init:
            for i in range(size):
                self.myElements[i]=((self.myName,i,random.random()))
    def checkRequests(self,element):
      if(element in self.pastRequests):
        return False;
      else:
        if len(self.pastRequests)==REQUESTS_CACHED:
          self.pastRequests=self.pastRequests[1:]
          self.pastRequests.append(element)
          return True
        else:
          toss=2    
    def numElements(self):
        #return len(self.myElements.keys())
        return DATASIZE_PER_HOST
    def numFilled(self):
        return len(self.myElements.keys())

#mid means Message ID
class Message(object):
    def __init__(self, mid=-1):
        self.myId=mid
#Tell host about another host. hostInfo contains the socket details of another host
class ServerSayGoMessage(Message):
    def __init(self):
        self.myId=0

class ServerHostAlertMessage(Message):
    def __init__(self,mid=1,hostInfo=None,hostName=None):
        self.myId=mid
        self.myHostInfo=hostInfo
        self.myHostName=hostName
#This tells a host "listen on this port for messages." This is a bit iffy
class ServerHostListenMessage(Message):
    def __init__(self,mid=2,listenInfo=None,numPorts=0):
        self.myId=mid
        self.myListenInfo=listenInfo
        self.myNumPorts=numPorts

#This tells a host to update their probability distributions
class ServerProbabilityUpdateMessage(Message):
    #probId is probability ID. If we have multiple distributions we might update, this is where we'll tell the host "update THIS distribution"
    #distribution should be a dictionary of dataset ID's to probabilities which should sum to 1 for my sanity
    def __init__(self,mid=3,probId=-1,distribution=None):
        self.myId=mid
        self.myProbId=probId
        self.myDistribution=distribution

class ClientRequestDataMessage(Message):
    #dataset says which dataset to be aware of
    #element says "give me THAT element in the dataset"
    def __init__(self,mid=4,dataSet=None,element=None):
        self.myId=mid
        self.myDataSet=dataSet
        self.myElement=element

class ClientResponseMessage(Message):
    #element will be none if we don't have the element, the element otherwise (imagine that)
    def __init__(self,mid=5,element=None, allowKeep=True):
        self.myId=mid
        self.myDataSet=dataSet
        self.myElement=element
        self.myKeepable=allowKeep

class ClientRequestDeletion(Message):
    #dataset says which dataset to be aware of
    #element says "delete THAT element in the dataset"
    def __init__(self,mid=6,dataSet=None,element=None):
        self.myId=mid
        self.myDataSet=dataSet
        self.myElement=element

class ClientSayEhlo(Message):
    def __init__(self,mid=7):
        self.myId=mid
class ServerRegisterDataSet(Message):
    def __init__(self,mid=8,name="None Given",elementSet={}):
        self.myId=mid
        self.myName=name
        self.myElements=elementSet


def send(channel, *args):
    buf = marshall(args)
    value = socket.htonl(len(buf))
    size = struct.pack("L",value)
    channel.send(size)
    channel.send(buf)

def receive(channel):

    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error, e:
        return ''

    buf = ""

    while len(buf) < size:
        buf = channel.recv(size - len(buf))

    return unmarshall(buf)[0]
