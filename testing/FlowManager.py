import pdb
import random
import sys

class DistributedGroup:
  def __init__(self):
    self.myHosts={}
    self.myFlowGraph={}
    self.hostIndex=0
    self.numTransfersSinceChange=0
  def addHost(self,host):
    self.myHosts[host.myId]=host
    self.hostIndex+=1
    host.myManager=self
    host.myReturnProbs={}
  def groupInitialize(self):
    for fromHost in self.myHosts:
      for toHost in self.myHosts:
        if(fromHost==toHost):
          continue
        prob=1.0/len(self.myHosts[toHost].myDataSets.keys())
        for key in self.myHosts[toHost].myDataSets.keys(): #IF FROM HOST AND TO HOST KNOW ABOUT DIFFERENT DATA SETS THAT'S WHY THIS IS BREAKING
          self.myHosts[fromHost].myReturnProbs[(self.myHosts[toHost].myId,key)]=prob
  def manage(self):
    self.numTransfersSinceChange+=1
    if (self.numTransfersSinceChange<100):
      return
    for hostKey in self.myHosts.keys():
      self.myHosts[hostKey].printSetData()
    self.numTransfersSinceChange=0  

class DataSet:
  def __init__(self,name="None Given",init=True):
    self.myName=name
    self.myElements={}
    if init:
      for i in range(100):
        self.myElements[i]=((self.myName,i,random.random()))

  def numElements(self):
    #return len(self.myElements.keys())
    return 100
            
class Host:
  def __init__(self,dataSets=None):
    self.myDataSets={}
    self.myProbabilities={}
    self.myId=random.random() #if this collides, God doesn't want this to work anyway. TODO: make less awful
    if dataSets != None:
      for setName in dataSets:
        name=setName.myName
        self.myDataSets[name]=setName
        self.myProbabilities[name]=0.0
  def printSetData(self):
    print self.myId
    for key in self.myDataSets.keys():
      print str(key)+" "+str(len(self.myDataSets[key].myElements.keys()))
    print "\n"
  def addProbability(self, name, probability):
    self.myProbabilities[name] = probability

  def chooseDataSet(self,distribution):
    r = random.random()
    sum=distribution[distribution.keys()[0]]
    i=1
    while(r>sum):
      sum+=distribution[distribution.keys()[i]]
      i+=1
    i-=1
    return distribution.keys()[i]

  def chooseElement(self, setName):
    r = random.random()
    idx = self.myDataSets[setName].numElements() * r
    #return self.myDataSets[setName].myElements[int(idx)]
    return int(idx)
  #def chooseExistingElement(self,setName):
  #  r = random.random()
  #  pdb.set_trace()
  #  idx = len(self.myDataSets[setName].myElements.keys())*r
  #  #return self.myDataSets[setName].myElements[int(idx)]
  #  return self.myDataSets[setName].myElements.keys()[int(idx)]
  def chooseExistingElement(self,choiceSet):
    r = random.random()
    idx = len(choiceSet.keys())*r
    #return self.myDataSets[setName].myElements[int(idx)]
    return choiceSet.keys()[int(idx)]
  def addSet(self,setName):
    self.myDataSets[setName.myName]=setName

  def addSetByName(self,name):
    self.myDataSets[name]=DataSet(name, False)

  def send(self,setName,num,host):
    host.receive(self.myDataSets[setName].myElements[num])
    del self.myDataSets[setName].myElements[num]
    if(self.myManager):
      if(self.myManager.myHosts.has_key(host.myId)):
        if(self.myManager.myFlowGraph.has_key((self.myId,host.myId,setName))):
          self.myManager.myFlowGraph[(self.myId,host.myId,setName)]=self.myManager.myFlowGraph[(self.myId,host.myId,setName)]+1
        else:
          self.myManager.myFlowGraph[(self.myId,host.myId,setName)]=1
      else:
        print "Manager action requested on unknown host"
    self.myManager.manage()

  def sendWithoutDel(self,setName,num,host):
    host.receive(self.myDataSets[setName].myElements[num])
    if(self.myManager):
      if(self.myManager.myHosts.has_key(host.myId)):
        if(self.myManager.myFlowGraph.has_key((self.myId,host.myId,setName))):
          self.myManager.myFlowGraph[(self.myId,host.myId,setName)]=self.myManager.myFlowGraph[(self.myId,host.myId,setName)]+1
        else:
          self.myManager.myFlowGraph[(self.myId,host.myId,setName)]=1
      else:
        print "Manager action requested on unknown host"
    self.myManager.manage()
  def receive(self,element):
    name,num,val=element
    if not self.myDataSets.has_key(name):
      self.myDataSets[name]={}
    if not self.myDataSets[name].myElements.has_key(num):
      self.myDataSets[name].myElements[num]=(name,num,val)

  def request(self,host,setName,element):
    if not host.myDataSets.has_key(setName):
      return None
    if not host.myDataSets[setName].myElements.has_key(element):
      return None
    host.sendWithoutDel(setName,element,self)
    r = random.random()
    # TODO: copy returnProbs, then rescale distribution after removing the prob for the set we receive from
    if r < self.myProbabilities[setName] :
      newProbs=self.myReturnProbs.copy()
      del newProbs[(host.myId,setName)]
      scalar=0.0
      for key in newProbs.keys():
         scalar+=newProbs[key]
      for key in newProbs.keys():
         newProbs[key]=newProbs[key]/scalar
      ds=self.chooseDataSet(newProbs)
      hostId,setName=ds
      elem= self.chooseExistingElement(self.myDataSets[setName].myElements)
      self.send(setName,elem,host)
      self.requestDeletion(host,setName,element)
    else:
      del self.myDataSets[setName].myElements[element] 

  def requestDeletion(self,host,setName,element):
    if not host.myDataSets.has_key(setName):
      print "MISS"
      pdb.set_trace()
      return None
    if not host.myDataSets[setName].myElements.has_key(element):
      print "MISS"
      pdb.set_trace()
      return None
    del host.myDataSets[setName].myElements[element]
