import sys

filename1 = sys.argv[1]
filename2 = sys.argv[2]
f1 = open(filename1, 'r')
f2 = open(filename2, 'r')

h1 = []
h2 = []
tup = []
time1 = []
time2 = []

for line in f1:
  if (line.startswith("TIME")):
    timesp = line.split(":")
    time1.append(float(timesp[1]))
    
  if (line.startswith("In dataset")):
    linesp = line.split(":")
    tup.append(int(linesp[1]))

  if len(tup) == 4:
    h1.append(tup)
    tup = []

for line in f2:
  if (line.startswith("TIME")):
    timesp = line.split(":")
    time2.append(float(timesp[1]))

  if (line.startswith("In dataset")):
    linesp = line.split(":")
    tup.append(int(linesp[1]))

  if len(tup) == 4:
    h2.append(tup)
    tup = []


line11 = []
line21 = []
line31 = []
line41 = []
line12 = []
line22 = []
line32 = []
line42 = []
for t in h1:
  line11.append(t[0]) 
  line21.append(t[1]) 
  line31.append(t[2]) 
  line41.append(t[3]) 

for t in h2:
  line12.append(t[0]) 
  line22.append(t[1]) 
  line32.append(t[2]) 
  line42.append(t[3]) 

import pdb; pdb.set_trace()
 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


width = 1     # the width of the bars
N1 = len(line11)
N2 = len(line12)
ind1 = np.arange(N1)  # the x locations for the groups
ind2 = np.arange(N2)  # the x locations for the groups
fig = plt.figure(dpi=200)
ax1 = plt.subplot(211)
plt.axis([0, 120, 10, 140])
plt.plot(time1, line11, lw=1, color='blue')
plt.plot(time1, line21, lw=1, color='green')
plt.plot(time1, line31, lw=1, color='red')
plt.plot(time1, line41, lw=1, color='purple')

ax1 = plt.subplot(212)
plt.axis([0, 120, 10, 140])
plt.plot(time2, line12, lw=1, color='blue')
plt.plot(time2, line22, lw=1, color='green')
plt.plot(time2, line32, lw=1, color='red')
plt.plot(time2, line42, lw=1, color='purple')

plt.show()
