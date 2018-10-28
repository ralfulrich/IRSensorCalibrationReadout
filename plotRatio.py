#!/usr/bin/python

import os, sys
import re

import numpy as np
from numpy import ma

from scipy.interpolate import InterpolatedUnivariateSpline
from scipy import interpolate

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib import colors, ticker, cm

import pickle
import math

from plotDataLib import *


def getPeakSignal(histData2D_rel, xedges_rel, yedges_rel):
        
    # horizontal slice, to find x position of sensor FIT
    xVoltage = np.array(histData2D_rel.T[findBin(yedges_rel, (yedges_rel[0]+yedges_rel[-1])/4 )])
    xSlice = np.linspace(xedges_rel[0], xedges_rel[-1], num=len(xedges_rel)-1)
    xMaxSignalIs, xMaxSignalAt = findMaximum(xSlice[1:-2], xVoltage[1:-2]) # exclude edges
    xMaxBin = findBin(xedges_rel, xMaxSignalAt)
    
    if not xMaxBin:
        return None
    
    # vertical slice FIT
    dist = np.linspace(yedges_rel[0], yedges_rel[-1], num=len(yedges_rel)-1)
    voltage = np.array(histData2D_rel.T[:,findBin(xedges_rel, xMaxSignalAt)]) 
    maxSignalIs, maxSignalAt = findMaximum(dist[0:-2], voltage[0:-2]) # exclude tail
    print ("maxIs/at=" + str(maxSignalIs) + " " + str(maxSignalAt))    

    return maxSignalIs
    

# --------------- start main program ---------------------

if (len(sys.argv)<3):
    print "Please give at least two valid data files!"
    sys.exit()

filename0 = str(sys.argv[1])
pars0,nbinsx0,nbinsy0,xmin0,xmax0,ymin0,ymax0,histData2D0,xedges0,yedges0,x0,y0,V0 = loadData(filename0)
histData2D_ref, xedges_ref, yedges_ref = np.histogram2d(x0, y0, bins=[nbinsx0,nbinsy0] , range=[[xmin0,xmax0],[ymin0,ymax0]], normed=False, weights=V0)    
maxSignalRef = getPeakSignal(histData2D_ref, xedges_ref, yedges_ref)
I_ref = pars0['Iin']

xcenters0 = [(xedges0[i] + xedges0[i+1])/2 for i in range(len(xedges0)-1) ]
ycenters0 = [(yedges0[i] + yedges0[i+1])/2 for i in range(len(yedges0)-1) ]
#print str(xcenters0), str(len(xcenters0))
#print str(ycenters0), str(len(ycenters0))
#print str(len(histData2D0.astype(float).T))
#for r in histData2D0.astype(float).T: print str(len(r))
try:
    histData2D0_interpolate = interpolate.interp2d(xcenters0, ycenters0, histData2D0.astype(float).T, kind='cubic')
except:
    print "cannot intepolte data of " + filename0
    sys.exit()

#print "f0=" + str(f0(10,10))
#print str(xedges0), str(len(xedges0))
#print str(V0), str(len(V0))
#print str(histData2D0), str(len(histData2D0))
nfile = len(sys.argv) - 2

#fig, ax = plt.subplots(nfile,1)#,figsize=[6*nfile, 8])
fig = plt.figure(figsize=[6*nfile, 8])

I_mod = []
R_mod = []

for ifile in range(nfile):

    filename = str(sys.argv[ifile+2])
    pars,nbinsx,nbinsy,xmin,xmax,ymin,ymax,histData2D,xedges,yedges,x,y,V = loadData(filename)
    #xcenters = [(xedges[i] + xedges[i+1])/2 for i in range(len(xedges)-1) ]
    #ycenters = [(yedges[i] + yedges[i+1])/2 for i in range(len(yedges)-1) ]
    #f = interpolate.RectBivariateSpline(xcenters, ycenters, histData2D)

    xcenters = [(xedges[i] + xedges[i+1])/2 for i in range(len(xedges)-1) ]
    ycenters = [(yedges[i] + yedges[i+1])/2 for i in range(len(yedges)-1) ]
    try:
        histData2D_interpolate = interpolate.interp2d(xcenters, ycenters, histData2D.astype(float).T, kind='cubic')
    except:
        print "cannot interpolate data of " + filename
        continue

    
    V_rel = [0.0] * len(V)
    for iV in range(len(V)):
        Vref_inter = histData2D0_interpolate(x[iV], y[iV])[0]
        V_inter = histData2D_interpolate(x[iV], y[iV])[0]
        if (Vref_inter != 0):
            V_rel[iV] = V_inter / Vref_inter
    
    histData2D_rel, xedges_rel, yedges_rel = np.histogram2d(x, y, bins=[nbinsx,nbinsy] , range=[[xmin,xmax],[ymin,ymax]], normed=False, weights=V_rel)        
    maxSignalIs = getPeakSignal(histData2D_rel, xedges_rel, yedges_rel)
    print filename
    print str(maxSignalIs)

    if (maxSignalIs):
        I_mod.append(pars['Iin']/I_ref)
        R_mod.append(maxSignalIs) # /maxSignalRef)
    
    #fig, ax = plt.subplots(nrows=1, ncols=2, )
    ax = fig.add_subplot(1, nfile, ifile+1)
    ax.set_title("I=" + str(pars["Iin"]) + " mA, U=" + str(float(pars["Vin"])/1000.) + " V", fontsize=18)
    plt.imshow(histData2D_rel.T, origin='lower',interpolation='nearest', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap="ocean_r", vmin=0.7, vmax=1.3)
    plt.colorbar().set_label('ratio',fontsize=10)
    #    pc = ax.pcolorfast(xedges, yedges, hrel.T)

print "put these data into: plotCurrentDependence.py"
print str(I_mod)
print str(R_mod)


plt.show()
plt.tight_layout()
plt.savefig("Ratio.png", bbox_inches="tight")



