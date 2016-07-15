#!/usr/bin/python

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

filename = str(sys.argv[1])
with open(filename,'r') as f:

    xTmp = []
    yTmp = []
    VTmp = []
    for line in f:
        if line[0] == "#":
            continue
        data = line.split()
        values = []
        for i in data:
            values.append(float(i))
        xStep=values[0]
        yStep=values[1]
        xPos=values[2]
        yPos=values[3]
        nMeas0=int(values[4])
        Meas = 0.
        nMeas = 0
        for i in range(nMeas0):
            if values[5+i]  < 1e5:
                Meas +=values[5+i] 
                nMeas += 1
        Meas/= nMeas
        
        xTmp.append(xPos)
        yTmp.append(yPos)
        if Meas > 1e5:
            print "ERROR", xStep, yStep, Meas
            VTmp.append(0)
        else:
            VTmp.append(Meas)

nrows, ncols = 41, 41

x = np.array(xTmp)
y = np.array(yTmp)
V = np.array(VTmp)

grid = V.reshape((nrows, ncols))

fig = plt.figure(figsize=[8,8])
ax = fig.gca()

plt.xlabel('x [mm]',fontsize=18)
plt.ylabel('y [mm]',fontsize=18)
plt.title(str(sys.argv[2]),fontsize=18)

plt.imshow(grid, extent=(x.min(), x.max(), y.max(), y.min()),
           interpolation='nearest', cmap=cm.gist_earth)
plt.colorbar().set_label('voltage [mV]',fontsize=18)
plt.savefig("SensorData.png",bbox_inches="tight")
