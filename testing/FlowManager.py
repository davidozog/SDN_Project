import pdb
import random
import sys

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
		if dataSets != None:
			for set in dataSets:
				name=set.myName
				self.myDataSets[name]=set

	def send(self,set,num,host):
		host.receive(self.myDataSets[set].myElements[num])
		del self.myDataSets[set].myElements[num]

	def receive(self,element):
		name,num,val=element
		if not self.myDataSets.has_key(name):
			self.myDataSets[name]={}
		if not self.myDataSets[name].has_key(num):
			self.myDataSets[name][num]=val

		pdb.set_trace()
		
