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

import math

from plotDataLib import loadData

def getPar(line,pars,name) :
    if name not in line:
        return
    pos = line.find(name)
    pars[name] = float(re.split(',| |;|', line[pos+len(name):].strip())[0])


def findBin(vec, val):
    for i in range(len(vec)-1):
        if (vec[i]<=val and vec[i+1]>val):
            return i
    return None


def findBinCenter(vec, val):
    i = findBin(vec, val)
    return (vec[i] + vec[i+1]) / 2


def findMaximum(x_values, y_values) :
    f = InterpolatedUnivariateSpline(x_values, y_values, k=4)
    cr_pts = f.derivative().roots()
    cr_pts = np.append(cr_pts, (x_values[0], x_values[-1]))  # also check the endpoints of the interval
    cr_vals = f(cr_pts)
    min_index = np.argmin(cr_vals)
    max_index = np.argmax(cr_vals)    
    #print("Maximum value {} at {}\nMinimum value {} at {}".format(cr_vals[max_index], cr_pts[max_index], cr_vals[min_index], cr_pts[min_index]))
    return cr_pts[max_index]
    


# --------------- start main program ---------------------

if (len(sys.argv)<3):
    print "Please give at least two valid data files!"
    sys.exit()

filename0 = str(sys.argv[1])
pars,nbins,xmin,xmax,ymin,ymax,histData2D0,xedges0,yedges0,x0,y0,V0 = loadData(filename0)

#xcenters0 = [(xedges0[i] + xedges0[i+1])/2 for i in range(len(xedges0)-1) ]
#ycenters0 = [(yedges0[i] + yedges0[i+1])/2 for i in range(len(yedges0)-1) ]
#f0 = interpolate.RectBivariateSpline(xcenters0, ycenters0, histData2D0)

ifile = len(sys.argv)-2

fig = plt.figure(figsize=[6*ifile, 8])

for ifile in range(ifile):

    filename = str(sys.argv[ifile+2])
    pars,nbins,xmin,xmax,ymin,ymax,histData2D,xedges,yedges,x,y,V = loadData(filename)
    #xcenters = [(xedges[i] + xedges[i+1])/2 for i in range(len(xedges)-1) ]
    #ycenters = [(yedges[i] + yedges[i+1])/2 for i in range(len(yedges)-1) ]
    #f = interpolate.RectBivariateSpline(xcenters, ycenters, histData2D)


    V_rel = [0.0] * len(V)
    for iV in range(len(V)):
        if (V0[iV]!=0):
            V_rel[iV] = V[iV] / V0[iV]
    
    histData2D_rel, xedges_rel, yedges_rel = np.histogram2d(x, y, bins=nbins , range=[[xmin,xmax],[ymin,ymax]], normed=False, weights=V_rel)
    
    #fig, ax = plt.subplots(nrows=1, ncols=2)
    ax = fig.add_subplot(121)
    plt.imshow(histData2D_rel.T, origin='lower',interpolation='nearest', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap="ocean_r")
    plt.colorbar().set_label('voltage [mV]',fontsize=18)
    #    pc = ax.pcolorfast(xedges, yedges, hrel.T)

plt.show()
plt.tight_layout()
plt.savefig("Ratio.png", bbox_inches="tight")



