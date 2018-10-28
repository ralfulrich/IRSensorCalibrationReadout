#!/usr/bin/python

import os, sys
import re

import numpy as np
from numpy import ma

from scipy.interpolate import InterpolatedUnivariateSpline

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib import colors, ticker, cm

import math

def getPar(line,pars,name) :
    if name not in line:
        return
    pos = line.find(name)
    pars[name.strip('\n\r =;.,')] = float(re.split(',| |;|', line[pos+len(name):].strip())[0])


def findBin(vec, val):
    for i in range(len(vec)-1):
        if (vec[i]<=val and vec[i+1]>val):
            return i
    return None


def findBinCenter(vec, val):
    i = findBin(vec, val)
    return (vec[i] + vec[i+1]) / 2


##
## interpolate x/y data and find maximum position 
##
def findMaximum(x_values, y_values) :
    try:
        f = InterpolatedUnivariateSpline(x_values, y_values, k=4)
        cr_pts = f.derivative().roots()
        cr_pts = np.append(cr_pts, (x_values[0], x_values[-1]))  # also check the endpoints of the interval
        cr_vals = f(cr_pts)
        min_index = np.argmin(cr_vals)
        max_index = np.argmax(cr_vals)    
        #print("Maximum value {} at {}\nMinimum value {} at {}".format(cr_vals[max_index], cr_pts[max_index], cr_vals[min_index], cr_pts[min_index]))
        return cr_vals[max_index], cr_pts[max_index]
    except:
        print ("findMaximum failes for x_values=" + str(x_values) + " y_values=" + str(y_values))
        return None, None
    


def loadData(filename) :
    
    pars = dict()

    with open(filename, 'r') as f:
        
        xmin = 0.
        xmax = 0.
        ymin = 0.
        ymax = 0.
        first = True
        
        xTmp = []
        yTmp = []
        VTmp = []
        for line in f:
            if line[0] == "#":
                getPar(line, pars, "scanRangeX")
                getPar(line, pars, "scanRangeY")
                getPar(line, pars, "initialOffset")
                getPar(line, pars, "stepSize")
                getPar(line, pars, "sensorX")
                # scanRangeX 151.50 mm; scanRangeY  70.00 mm; stepSize   2.00 mm; initialOffset   4.00 mm; sensorX 155.00 mm; start position at (x|y)=(119.92|  0.00) mm
                getPar(line, pars, "Iin=")
                getPar(line, pars, "Vin=")
                getPar(line, pars, "T=")
                # Iin=    30.00 mA ,  Vin= 12151.10 mV, T=    18.74 C
                pars["initialOffset"] = 7 # mm
                continue
            data = line.split()
            values = []
            for i in data:
                values.append(float(i))
            Step=values[0]
            yStep=values[1]
            xPos=values[2]
            yPos=values[3] + pars['initialOffset']
            if (first):
                xmin = xPos
                xmax = xPos
                ymin = yPos
                ymax = yPos
                first = False
            else:
                xmin = min(xmin, xPos)
                xmax = max(xmax, xPos)
                ymin = min(ymin, yPos)
                ymax = max(ymax, yPos)                
    
            nMeas0=int(values[4])
            Meas = 0.
            nMeas = 0
            for i in range(nMeas0):
                if values[5+i] < 1e5:
                    Meas += values[5+i] 
                    nMeas += 1
            if nMeas != 0:
                Meas/= nMeas

            xTmp.append(xPos)
            yTmp.append(yPos)
            if Meas > 1e5:
                VTmp.append(0)
            else:
                VTmp.append(Meas)

    print (str(pars))

    x = np.array(xTmp)
    y = np.array(yTmp)
    V = np.array(VTmp)

    print "loadData> ", xmin, xmax, pars['stepSize'], (xmax-xmin) / pars['stepSize']
    xmin -= pars['stepSize'] / 2
    xmax += pars['stepSize'] / 2
    ymin -= pars['stepSize'] / 2
    ymax += pars['stepSize'] / 2
    nbinsx = math.floor((xmax-xmin) / pars['stepSize'] + 0.5) 
    nbinsy = math.floor((ymax-ymin) / pars['stepSize'] + 0.5) 
    #nbins = pars['scanRangeY'] / pars['stepSize']
    #xmin = pars['sensorX'] - pars['scanRangeY']/2 - pars['stepSize']/2
    #xmax = xmin + pars['stepSize']*nbins
    #ymin = pars['initialOffset'] - pars['stepSize']/2
    #ymax = ymin + pars['stepSize']*nbins
    histData2D, xedges, yedges = np.histogram2d(x, y, bins=[nbinsx,nbinsy] , range=[[xmin,xmax],[ymin,ymax]], normed=False, weights=V)

    return pars,nbinsx,nbinsy,xmin,xmax,ymin,ymax,histData2D,xedges,yedges,x,y,V



