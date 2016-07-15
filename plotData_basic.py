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
        data = line.split()
        values = []
        for i in data:
            values.append(float(i))
        xStep=values[0]
        yStep=values[1]
        xPos=values[2]
        yPos=values[3]
        nMeas=int(values[4])
        Meas = 0.
        for i in range(nMeas):
            Meas +=values[5+i] 
        Meas/= nMeas
        
        xTmp.append(xPos)
        yTmp.append(yPos)
        VTmp.append(Meas)

nrows, ncols = 3, 3

x = np.array(xTmp)
y = np.array(yTmp)
V = np.array(VTmp)
grid = V.reshape((nrows, ncols))


fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)
ax.set_title(filename)
plt.imshow(grid, extent=(x.min(), x.max(), y.max(), y.min()),
           interpolation='nearest', cmap=cm.gist_earth)
plt.colorbar(orientation='vertical')
plt.show()
