#!/usr/bin/python

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math
from matplotlib.patches import Ellipse

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
        Step=values[0]
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
        if nMeas != 0:
            Meas/= nMeas
        
        xTmp.append(xPos)
        yTmp.append(yPos)
        if Meas > 1e5:
            VTmp.append(0)
        else:
            VTmp.append(Meas)

print len(xTmp), len(yTmp), len(VTmp)

nrows, ncols = int(math.sqrt(len(xTmp))), int(math.sqrt(len(xTmp)))

x = np.array(xTmp)
y = np.array(yTmp)
V = np.array(VTmp)

grid = V.reshape((nrows, ncols))

fig = plt.figure(figsize=[8,8])
ax = fig.gca()

plt.xlabel('x [mm]',fontsize=18)
plt.ylabel('y [mm]',fontsize=18)
plt.title(filename[19:24-len(filename)],fontsize=18)

ax.set_xlim([x.min()-5,x.max()+5])
ax.set_ylim([y.min()-5,y.max()+30])

plt.imshow(grid, extent=(x.min(),x.max(),y.min(),y.max()), interpolation='nearest', cmap=cm.gist_earth)
plt.colorbar().set_label('voltage [mV]',fontsize=18)

ellipse = Ellipse(xy=(62,133), width=70, height=140, edgecolor='r', fc='None', lw=2)
beampipe = circle1=plt.Circle((62,133+4+(57+0.5)/2),(57+0.5)/2,color='black',fill=False,label="beam pipe",lw=2, ls="dashed")

ax.add_patch(ellipse)
ax.add_patch(beampipe)
ax.invert_xaxis()
plt.savefig("SensorData.png",bbox_inches="tight")
