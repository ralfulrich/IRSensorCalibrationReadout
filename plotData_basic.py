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

from plotDataLib  import *


#cal2015 = [2.3623, -27.256, 118.53, -232.03, 165.49 , 30.624, 0.,0.,0.]
#cal2015 = [30.624, 165.49, -232.03, 118.53, -27.256, 2.3623, 0., 0., 0.]
#cal2015 = [0., 0., 0., 30.624, 165.49, -232.03, 118.53, -27.256, 2.3623]


def plotData(filename, title, pdfName):

    pars,nbinsx,nbinsy,xmin,xmax,ymin,ymax,histData2D,xedges,yedges,x,y,V = loadData(filename)
    
    # horizontal slice FIT
    xVoltage = np.array(histData2D.T[findBin(yedges,20)])
    xSlice = np.linspace(xedges[0], xedges[-1], num=nbinsx)
    HorizontalPolfit= np.poly1d(np.polyfit(xSlice[1:], xVoltage[1:], 9))
    maxmaxSignalIs, maxSignalAt = findMaximum(xSlice[1:], xVoltage[1:])

    # vertical slice FIT
    dist = np.linspace(yedges[0], yedges[-1], num=nbinsy)
    voltage = np.array(histData2D.T[:,findBin(xedges, maxSignalAt)]) # pars['sensorX'])])
    param = np.polyfit(dist[findBin(dist,5):], voltage[findBin(dist,5):], 9)
    CentralPolfit= np.poly1d(param)



    #### Drawing

    # main 2d plot --------------
    fig = plt.figure(figsize=[16,8])
    ax1 = fig.add_subplot(131)
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
    ax2 = fig.add_subplot(232)
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
    ax3 = fig.add_subplot(235)
    ax3.set_xlabel('x [mm]',fontsize=18)
    ax3.set_xlim([xedges[1],xedges[-1]]) # x-interval
    ax3.set_ylim([0,histData2D.max()*1.2])
    ax3.set_title("horizontal slice",fontsize=18)
    data2, = plt.plot(xSlice, xVoltage , 'k.')
    fit2, = plt.plot(xSlice[0:], HorizontalPolfit(xSlice[0:]), 'g-',lw=2)

    #cal2015_line = np.poly1d(cal2015)
    #fit2015, = plt.plot(xSlice[0:], cal2015_line(xSlice[0:]), 'g-',lw=1)
    #print str(cal2015_line(20))+" "+ str(cal2015_line(30)) +" "+ str(cal2015_line(40)) +" "+ str(cal2015_line(50))    
    #plt.legend([data2, fit2, fit2015], ['data','pol9 fit', '2015'])



    # calibration fit plot --------------------
    ax2 = fig.add_subplot(233)
    ax2.set_xlim([-20,4000]) # mV
    ax2.set_ylim([-20, 80]) # mm 
    ax2.set_ylabel('distance [mm]', fontsize=18)
    ax2.set_xlabel('Voltage [mV]', fontsize=18)
    ax2.set_title("calibration", fontsize=18)
    data, = plt.plot(voltage, dist , 'k.')
#    fit, = plt.plot(dist[0:], CentralPolfit(dist[0:]), 'r-',lw=2)
#    plt.legend([data, fit], ['data','pol9 fit'])
#    text = ""
#    for i in range(10):
#        text +="p"+str(i)+" = "+str(param[i])+"\n"
#    ax2.text(-15, 100,text, fontsize=10)

    
    
    # ----------- print, save and display
    plt.tight_layout()
    plt.savefig("SensorData.png",bbox_inches="tight")
    #plt.savefig("SensorData_" + title + ".pdf", bbox_inches="tight")
    plt.savefig(pdfName, bbox_inches="tight")
    print ("output: " + pdfName)
    
    try:
        os.system("eog SensorData.png")
    except:
        pass




        
if (len(sys.argv)<2):
    print "Please give a valid data file!"
    sys.exit()


filename = str(sys.argv[1])
filepath,filename_w_ext = os.path.split(filename)
filename_wo_ext,file_extension = os.path.splitext(filename_w_ext)
if (filepath!=""):
    pdfName = filepath + "/" + filename_wo_ext+".pdf"
else:
    pdfName = filename_wo_ext+".pdf"

# sensor name...
title = filename[filename.rfind('/')+12:filename.rfind('/')+17]

plotData(filename, title, pdfName)

