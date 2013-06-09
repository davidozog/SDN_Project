LOAD_BAL_TYPE1 = 'orig'
LOAD_BAL_TYPE2 = 'ie_dlb'
LOAD_BAL_TYPE3 = 'zolt'
LOAD_BAL_TYPE4 = 'zolt'
f1 = open('good_data/tce_ccsd_benzene.orig.LB.t2_7.TZ.first_iter')
f2 = open('good_data/tce_ccsd_benzene.ie_dlb.LB.t2_7.TZ.new.first_iter.exec')
f3 = open('good_data/tce_ccsd_benzene.zoltan.LB.t2_7-newer.TZ.first_iter.exec')
f4 = open('good_data/tce_ccsd_benzene.zoltan.LB.t2_7-newer.TZ.last_iter.exec')

def average(values):
  """Computes the arithmetic mean of a list of numbers."""
  return sum(values, 0.0) / len(values)

lbdict1 = {}
lbdict2 = {}
lbdict3 = {}
lbdict4 = {}
lbmax1 = 0.0
lbmax2 = 0.0
lbmax3 = 0.0
lbmax4 = 0.0

for line in f1:
  #print line
  line = line.split()
  try:
    if (line[0].find(LOAD_BAL_TYPE1)>=0):
      lbdict1[int(line[2])] = float(line[6])
      if float(line[6]) > lbmax1:
        lbmax1 = float(line[6])
  except:
    pass
print lbdict1

for line in f2:
  #print line
  line = line.split()
  try:
    if (line[0].find(LOAD_BAL_TYPE2)>=0):
      lbdict2[int(line[1])] = float(line[4])
      if float(line[4]) > lbmax2:
        lbmax2 = float(line[4])
  except:
    pass
print lbdict2

for line in f3:
  #print line
  line = line.split()
  try:
    if (line[0].find(LOAD_BAL_TYPE3)>=0):
      lbdict3[int(line[1])] = float(line[4])
      if float(line[4]) > lbmax3:
        lbmax3 = float(line[4])
  except:
    pass
print lbdict3

for line in f4:
  #print line
  line = line.split()
  try:
    if (line[0].find(LOAD_BAL_TYPE4)>=0):
      lbdict4[int(line[1])] = float(line[4])
      if float(line[4]) > lbmax4:
        lbmax4 = float(line[4])
  except:
    pass
print lbdict4

#g = open('good_data/' + LOAD_BAL_TYPE + '_data.txt', 'w')
#
#for key, value in lbdict1.iteritems():
#  g.write(str(key) + ' ' +  str(value) + '\n')
#  
#g.close()

f1.close()
f2.close()
f3.close()
f4.close()
  

  #try:
  #  gflop = 2.0 * float(line[0]) * float(line[1]) * float(line[2]) * 1e-9
  #  tdict[line[5]].append(( float(line[3]), gflop ))
  #except:
  #  gflop = 2.0 * float(line[0]) * float(line[1]) * float(line[2]) * 1e-9
  #  tdict[line[5]] = [( float(line[3]), gflop )]


#tarray = []
#for k in tdict.iterkeys():
#  total_gflop = 0.0
#  total_time = 0.0
#  for v in tdict[k]:
#  #tdict[k] = sum(v[1])/sum(v[0]);
#    total_gflop = total_gflop + v[1]
#    total_time = total_time + v[0]
#  #tarray.append(total_gflop/total_time)
#
#  # this is actually total MFLOPS
#  tarray.append(total_gflop*1e6)


tarray1 = []
tarray2 = []
tarray3 = []
tarray4 = []
for k, v in lbdict1.iteritems():
  tarray1.append(v / lbmax1) 
for k, v in lbdict2.iteritems():
  tarray2.append(v / lbmax1) 
for k, v in lbdict3.iteritems():
  tarray3.append(v / lbmax1) 
for k, v in lbdict4.iteritems():
  tarray4.append(v / lbmax1) 
  

print max(tarray1)
print len(tarray1)
print max(tarray2)
print len(tarray2)
print max(tarray3)
print len(tarray3)
print max(tarray4)
print len(tarray4)


#!/usr/bin/env python
# a bar plot with errorbars
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


N1 = len(tarray1)
N2 = len(tarray2)
N3 = len(tarray3)
N4 = len(tarray4)
Means1 = tarray1
Means2 = tarray2
Means3 = tarray3
Means4 = tarray4

ind1 = np.arange(N1)  # the x locations for the groups
ind2 = np.arange(N2)  # the x locations for the groups
ind3 = np.arange(N3)  # the x locations for the groups
ind4 = np.arange(N4)  # the x locations for the groups
width = 1     # the width of the bars

fig = plt.figure(dpi=200)
#plt.ylabel('Normalized Execution Time')
ax1 = plt.subplot(411)
#ax1 = fig.add_subplot(311)
#ax2 = fig.add_subplot(312)
#ax3 = fig.add_subplot(313)
rects1 = ax1.bar(ind1, Means1, width, color='b')
#rects2 = ax2.bar(ind, Means2, width, color='b')
#rects3 = ax3.bar(ind, Means3, width, color='b')
plt.setp(plt.gca(), 'xticklabels', [])
#plt.setp(plt.yticks()[1], rotation=30)
#plt.setp(plt.yticks()[1], rotation=30)
ax1.set_ylabel('(a)', rotation=0, position=(-3.0,0.5))
plt.setp(plt.gca(), yticks=(0.0,1.0))

# add some
plt.axis([0, len(tarray1), 0, 1.1])
#ax1.set_ylabel('Normalized Execution Time')
ax2 = plt.subplot(412)
rects2 = ax2.bar(ind2, Means2, width, color='b')
plt.setp(plt.gca(), 'xticklabels', [])
ax2.set_ylabel('(b)', rotation=0)
maxar = np.ones(N2)*(lbmax2/lbmax1)
plt.plot(ind2, maxar, lw=1, color='black', ls='--')
plt.setp(plt.gca(), yticks=(0.67, 1))

#ax.ticklabel_format(style='sci', scilimits=(0,0), axis='y') 

#ax.set_title('Scores by group and gender')
#ax.set_xticks(ind+width)
#ax.set_xticklabels( ('G1', 'G2', 'G3', 'G4', 'G5') )
plt.axis([0, len(tarray1), 0, 1.1])

ax3 = plt.subplot(413)
rects3 = ax3.bar(ind3, Means3, width, color='b')
plt.setp(plt.gca(), 'xticklabels', [])
plt.setp(plt.gca(), yticks=(0.49,1))
plt.axis([0, len(tarray1), 0, 1.1])
ax3.set_ylabel('(c)', rotation=0)
maxar = np.ones(N3)*(lbmax3/lbmax1)
plt.plot(ind3, maxar, lw=1, color='black', ls='--')

ax4 = plt.subplot(414)
rects4 = ax4.bar(ind4, Means4, width, color='b')
maxar = np.ones(N4)*(lbmax4/lbmax1)
plt.plot(ind4, maxar, lw=1, color='black', ls='--')
plt.setp(plt.gca(), yticks=(0.41,1))
plt.axis([0, len(tarray4), 0, 1.1])

ax4.set_ylabel('(d)', rotation=0)
ax4.set_xlabel('Process ID')

#ax.legend( rects1[0], 'Men') )

#def autolabel(rects):
#    # attach some text labels
#    for rect in rects:
#        height = rect.get_height()
#        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
#                ha='center', va='bottom')
#
#autolabel(rects1)
#autolabel(rects2)

plt.show()

#plt.savefig('taskload.png', dpi=200)

