import sys

def get_data(data_file):
  for line in f1:
    line = line.strip()
    if (line.startswith("TOTALFLOWAMOUNT")):
      linesp = line.split(":")
      linesp[1] = linesp[1].strip()
      linesp[2] = linesp[2].strip()
      time1.append(float(linesp[1]))
      d1.append(int(linesp[2]))
    

filename1 = sys.argv[1]
filename2 = sys.argv[2]
f1 = open(filename1, 'r')
f2 = open(filename2, 'r')

d1 = []
d2 = []
time1 = []
time2 = []

control = []
control2 = []

for line in f1:
  line = line.strip()
  if (line.startswith("TOTALFLOWAMOUNT")):
    linesp = line.split(":")
    linesp[1] = linesp[1].strip()
    linesp[2] = linesp[2].strip()
    time1.append(float(linesp[1]))
    d1.append(int(linesp[2]))

  if (line.startswith("CONTROLCHANNELFLOWAMOUNT")):
    linesp = line.split(":")
    linesp[1] = linesp[1].strip()
    linesp[2] = linesp[2].strip()
    control.append(int(linesp[2]))

for line in f2:
  line = line.strip()
  if (line.startswith("TOTALFLOWAMOUNT")):
    linesp = line.split(":")
    linesp[1] = linesp[1].strip()
    linesp[2] = linesp[2].strip()
    time2.append(float(linesp[1]))
    d2.append(int(linesp[2]))

  if (line.startswith("CONTROLCHANNELFLOWAMOUNT")):
    linesp = line.split(":")
    linesp[1] = linesp[1].strip()
    linesp[2] = linesp[2].strip()
    control2.append(int(linesp[2]))


line1 = []
line2 = []
for t in control:
  line1.append(t) 

for t in control2:
  line2.append(t) 

import pdb; pdb.set_trace()
 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


width = 1     # the width of the bars
N1 = len(line1)
N2 = len(line2)
#ind1 = np.arange(N1)  # the x locations for the groups
#ind2 = np.arange(N2)  # the x locations for the groups
fig = plt.figure(dpi=200)
#ax1 = plt.subplot(211)
plt.plot(time1, line1, lw=1, color='blue', label='mmp')
plt.plot(time2, line2, lw=1, color='red', label='app-only')
plt.legend()

plt.show()
