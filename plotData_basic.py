#!/usr/bin/python

import os, sys

import numpy as np
from numpy import ma

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib import colors, ticker, cm

import math

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

x = np.array(xTmp)
y = np.array(yTmp)
V = np.array(VTmp)

H, xedges, yedges = np.histogram2d(x, y, bins=101 , range=[[24.5,125.5],[39.5,140.5]], normed=False, weights=V)

dist = np.linspace(-1*(yedges[0]-133)+4, -1*(yedges[-1]-133)+4, num=101)
voltage = np.array(H.T[:,37])
param = np.polyfit(dist[40:-8], voltage[40:-8], 9)
CentralPolfit= np.poly1d(param)

xVoltage = np.array(H.T[80])
xSlice = np.linspace(xedges[0]-62, xedges[-1]-62, num=101)
HorizontalPolfit= np.poly1d(np.polyfit(xSlice[15:-40], xVoltage[15:-40], 9))
#### Drawing

fig = plt.figure(figsize=[12,8])
ax1 = fig.add_subplot(121)
ax1.set_xlim([x.min()-5,x.max()+5])
ax1.set_ylim([y.min()-5,y.max()+30])
ax1.set_xlabel('x [mm]',fontsize=18)
ax1.set_ylabel('y [mm]',fontsize=18)
ax1.invert_xaxis()
ax1.set_title(filename[19:24-len(filename)],fontsize=18)
plt.imshow(H.T, origin='lower',interpolation='nearest', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap="ocean_r")
plt.colorbar().set_label('voltage [mV]',fontsize=18)
ellipse = Ellipse(xy=(62,133), width=70, height=140, edgecolor='r', fc='None', lw=2)
beampipe = circle1=plt.Circle((62,133+4+(57+0.5)/2),(57+0.5)/2,color='black',fill=False,label="beam pipe",lw=2, ls="dashed")
xslice, = plt.plot([30,100],[yedges[80]+0.5,yedges[80]+0.5],'g--')
yslice, = plt.plot([xedges[37]+0.5,xedges[37]+0.5],[133,60],'r--')
ax1.add_patch(ellipse)
ax1.add_patch(beampipe)
ax1.invert_xaxis()
plt.legend([ellipse, beampipe, yslice], ['scan range','beampipe','slices'],loc=9)
plt.tight_layout()

ax2 = fig.add_subplot(222)
ax2.set_xlim([-20,80])
ax2.set_ylim([0,3000])
ax2.set_xlabel('distance [mm]',fontsize=18)
#ax2.set_ylabel('Voltage [mV]',fontsize=18)
ax2.set_title("vertical slice",fontsize=18)
data, = plt.plot(dist, voltage , 'k.')
fit, = plt.plot(dist[40:-8], CentralPolfit(dist[40:-8]), 'r-',lw=2)
plt.legend([data, fit], ['data','pol9 fit'])
text = ""
for i in range(10):
    text +="p"+str(i)+" = "+str(param[i])+"\n"
ax2.text(-15, 100,text, fontsize=10)

ax3 = fig.add_subplot(224)
ax3.set_xlabel('x [mm]',fontsize=18)
ax3.set_xlim([-40,40])
ax3.set_ylim([0,3000])
ax3.set_title("horizontal slice",fontsize=18)
data2, = plt.plot(xSlice, xVoltage , 'k.')
fit2, = plt.plot(xSlice[15:-40], HorizontalPolfit(xSlice[15:-40]), 'g-',lw=2)
plt.legend([data2, fit2], ['data','pol9 fit'])

plt.tight_layout()
plt.savefig("SensorData.png",bbox_inches="tight")
plt.savefig("SensorData_"+filename[19:24-len(filename)]+".pdf",bbox_inches="tight")

os.system("eog SensorData.png")
