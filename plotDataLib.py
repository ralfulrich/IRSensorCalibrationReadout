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



def loadData(filename) :
    
    pars = dict()

    with open(filename, 'r') as f:

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
                if values[5+i] < 1e5:
                    Meas += values[5+i] 
                    nMeas += 1
            if nMeas != 0:
                Meas/= nMeas

            xTmp.append(xPos)
            yTmp.append(yPos + pars['initialOffset'])
            if Meas > 1e5:
                VTmp.append(0)
            else:
                VTmp.append(Meas)

    print (str(pars))

    x = np.array(xTmp)
    y = np.array(yTmp)
    V = np.array(VTmp)

    nbins = pars['scanRangeY'] / pars['stepSize']
    xmin = pars['sensorX'] - pars['scanRangeY']/2 - pars['stepSize']/2
    xmax = xmin + pars['stepSize']*nbins
    ymin = pars['initialOffset'] - pars['stepSize']/2
    ymax = ymin + pars['stepSize']*nbins
    histData2D, xedges, yedges = np.histogram2d(x, y, bins=nbins , range=[[xmin,xmax],[ymin,ymax]], normed=False, weights=V)

    return pars,nbins,xmin,xmax,ymin,ymax,histData2D,xedges,yedges,x,y,V



def plotData(filename, title, pdfName):

    pars,nbins,xmin,xmax,ymin,ymax,histData2D,xedges,yedges,x,y,V = loadData(filename)
    
    # horizontal slice FIT
    xVoltage = np.array(histData2D.T[findBin(yedges,20)])
    xSlice = np.linspace(xedges[0], xedges[-1], num=nbins)
    HorizontalPolfit= np.poly1d(np.polyfit(xSlice[1:], xVoltage[1:], 9))
    maxSignalAt = findMaximum(xSlice[1:], xVoltage[1:])

    # vertical slice FIT
    dist = np.linspace(yedges[0], yedges[-1], num=nbins)
    voltage = np.array(histData2D.T[:,findBin(xedges, maxSignalAt)]) # pars['sensorX'])])
    param = np.polyfit(dist[findBin(dist,5):], voltage[findBin(dist,5):], 9)
    CentralPolfit= np.poly1d(param)



    #### Drawing

    # main 2d plot --------------
    fig = plt.figure(figsize=[12,8])
    ax1 = fig.add_subplot(121)
    ax1.set_xlim([xedges.min()-5, xedges.max()+5])
    ax1.set_ylim([yedges.min()-10, yedges.max()+30])
    ax1.set_xlabel('x [mm]',fontsize=18)
    ax1.set_ylabel('y [mm]',fontsize=18)
    ax1.invert_xaxis()
    ax1.set_title(title,fontsize=18)
    plt.imshow(histData2D.T, origin='lower',interpolation='nearest', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap="ocean_r")
    plt.colorbar().set_label('voltage [mV]',fontsize=18)

    ellipse = Ellipse(xy=(pars['sensorX'], pars['initialOffset']), width=70, height=140, edgecolor='b', fc='None', lw=1)
    beampipe = circle1=plt.Circle((pars['sensorX'], -(57+0.5)/2), (57+0.5)/2, color='black',fill=False,label="beam pipe",lw=2, ls="dashed")

    xslice, = plt.plot([xedges[1],xedges[-1]], [findBinCenter(yedges,20),findBinCenter(yedges,20)], 'r--')
    yslice, = plt.plot([findBinCenter(xedges,maxSignalAt),findBinCenter(xedges,maxSignalAt)], [yedges[1],yedges[-1]], 'r--')
    #yslice, = plt.plot([findBinCenter(xedges,pars['sensorX']),findBinCenter(xedges,pars['sensorX'])], [yedges[1],yedges[-1]], 'r--')
    ax1.add_patch(ellipse)
    ax1.add_patch(beampipe)
    ax1.invert_xaxis()
    plt.legend([ellipse, beampipe, yslice], ['scan range','beampipe','slices'],loc=9)
    plt.tight_layout()

    # horizontal fit plot --------------------
    ax2 = fig.add_subplot(222)
    ax2.set_xlim([-20,80]) # distance
    ax2.set_ylim([0,histData2D.max()*1.2]) 
    ax2.set_xlabel('distance [mm]',fontsize=18)
    #ax2.set_ylabel('Voltage [mV]',fontsize=18)
    ax2.set_title("vertical slice",fontsize=18)
    data, = plt.plot(dist, voltage , 'k.')
    fit, = plt.plot(dist[0:], CentralPolfit(dist[0:]), 'r-',lw=2)
    plt.legend([data, fit], ['data','pol9 fit'])
    text = ""
    for i in range(10):
        text +="p"+str(i)+" = "+str(param[i])+"\n"
    ax2.text(-15, 100,text, fontsize=10)

    # vertical fit plot --------------------------
    ax3 = fig.add_subplot(224)
    ax3.set_xlabel('x [mm]',fontsize=18)
    ax3.set_xlim([xedges[1],xedges[-1]]) # x-interval
    ax3.set_ylim([0,histData2D.max()*1.2])
    ax3.set_title("horizontal slice",fontsize=18)
    data2, = plt.plot(xSlice, xVoltage , 'k.')
    fit2, = plt.plot(xSlice[0:], HorizontalPolfit(xSlice[0:]), 'g-',lw=2)
    plt.legend([data2, fit2], ['data','pol9 fit'])

    # ----------- print, save and display
    plt.tight_layout()
    plt.savefig("SensorData.png",bbox_inches="tight")
    #plt.savefig("SensorData_" + title + ".pdf", bbox_inches="tight")
    plt.savefig(pdfName, bbox_inches="tight")

    try:
        os.system("eog SensorData.png")
    except:
        pass

