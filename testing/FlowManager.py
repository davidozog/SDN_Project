import pdb
import random
import sys

class DataSet:
	def __init__(self):
		self.myName="a"
		self.myElements={}
		for i in range(100):
			self.myElements[i]=((self.myName,i,random.random()))
	def numElements(self):
		return len(self.myElements.keys())
	
	        	
					
class Host:
	def __init__(self):
		myDataSets={}

	def send(self,set,num,host):
		host.receive(myElements[i])
		del self.myElements[num]

	def receive(self):
		h
