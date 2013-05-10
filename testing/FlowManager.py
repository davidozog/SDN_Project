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
	def manage(self):
		self.numTransfersSinceChange+=1
		if (self.numTransfersSinceChange<100):
			return
		print(self.myFlowGraph)
		numTransfersSinceChange=0	
class DataSet:
	def __init__(self,name="None Given",init=True):
		self.myName=name
		self.myElements={}
		if init:
			for i in range(100):
				self.myElements[i]=((self.myName,i,random.random()))

	def numElements(self):
		return len(self.myElements.keys())
	
	        	
					
class Host:
	def __init__(self,dataSets=None):
		self.myDataSets={}
		self.myProbabilities={}
		self.myId=random.random() #if this collides, God doesn't want this to work anyway. TODO: make less awful
		if dataSets != None:
			for set in dataSets:
				name=set.myName
				self.myDataSets[name]=set
				self.myProbabilities[name]=0.0
	def addSet(self,set):
		self.myDataSets[set.myName]=set
	def send(self,set,num,host):
		host.receive(self.myDataSets[set].myElements[num])
		del self.myDataSets[set].myElements[num]
		if(self.myManager):
			if(self.myManager.myHosts.has_key(host.myId)):
				if(self.myManager.myFlowGraph.has_key((self.myId,host.myId,set))):
					self.myManager.myFlowGraph[(self.myId,host.myId,set)]=self.myManager.myFlowGraph[(self.myId,host.myId,set)]+1
				else:
					self.myManager.myFlowGraph[(self.myId,host.myId,set)]=1
			else:
				print "Manager action requested on unknown host"
		self.myManager.manage()
	def receive(self,element):
		name,num,val=element
		if not self.myDataSets.has_key(name):
			self.myDataSets[name]={}
		if not self.myDataSets[name].has_key(num):
			self.myDataSets[name][num]=val

	def request(self,host,set,element):
		if not host.myDataSets.has_key(set):
			return None
		if not host.myDataSets[set].has_key(element):
			return None
		return host.myDataSets[set][element]
		
	def requestDeletion(self,host,set,element):
		if not host.myDataSets.has_key(set):
			return None
		if not host.myDataSets[set].has_key(element):
			return None
		del host.myDataSets[set][element]
