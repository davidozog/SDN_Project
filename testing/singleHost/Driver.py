from FlowManager import *

import sys
import pdb

def main():

  #pdb.set_trace()

  hostDict = {}
  set_a = DataSet("a")
  set_b = DataSet("b")

  host_a = Host([set_a])
  host_b = Host([set_b])

  myGroup = DistributedGroup()

  host_a.addSetByName("b")
  host_b.addSetByName("a")

  host_a.addProbability("a", 0.50)
  host_a.addProbability("b", 0.50)

  host_b.addProbability("a", 0.05)
  host_b.addProbability("b", 0.95)

  myGroup.addHost(host_a)
  myGroup.addHost(host_b)
  myGroup.groupInitialize()
  for i in range(50):
    host_a.send('a',i,host_b)
    host_b.send('b',i,host_a)
    myGroup.requestsSinceUpdate=0
    myGroup.numTransfersSinceChange=0 
  iter =0
  oldIter=0
  perfhistory=[]
  while True:
    dataset1 = host_a.chooseDataSet(host_a.myProbabilities)
    dataset2 = host_b.chooseDataSet(host_b.myProbabilities)

    elem1 = host_a.chooseElement(dataset1)
    elem2 = host_b.chooseElement(dataset2)
    host_a_done = False
    host_b_done = False
     
    if host_a.myDataSets[dataset1].myElements.has_key(elem1):
      host_a_done = True  
      myGroup.requestsSinceUpdate+=1
    else:
      host_a.request(host_b, dataset1, elem1)
  
    if host_b.myDataSets[dataset2].myElements.has_key(elem2):
      host_b_done = True  
      myGroup.requestsSinceUpdate+=1
    else: 
      host_b.request(host_a, dataset2, elem2)
    iter+=1
    if(iter==10000):
      perfhistory.append(myGroup.requestsSinceUpdate)
      pdb.set_trace()
    if(myGroup.updated):
      #print str(iter-oldIter)
      perfhistory.append(myGroup.requestsSinceUpdate)
      oldIter=iter
      myGroup.updated=False
      myGroup.requestsSinceUpdate=0
  #print dataset1
  #print dataset2

    
  for i in range(100):
    host_a.send('a',i,host_b)

  pdb.set_trace()

  
if __name__=="__main__":
  sys.exit(main())
