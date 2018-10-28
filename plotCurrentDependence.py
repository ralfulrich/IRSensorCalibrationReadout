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

# data 2018/syst, IR1
I_IR1 = [1,0.8623167576889911, 0.717160103478011, 0.5754527162977867, 0.42569703937913195] #, 1.0045990227076746, 1.0048864616269044]
R_IR1  =[1,0.94290235988354276, 0.87415292114427789, 0.79716368394782, 0.72092354909498135] #, 1.0065007243273778, 1.0055941762256622]
# data 2018/syst, IR2
I_IR2 = [1,0.8623167576889911, 0.717160103478011, 0.5754527162977867, 0.42569703937913195] #, 1.0045990227076746, 1.0048864616269044]
R_IR2 = [1,0.94344653598890327, 0.87500190970295522, 0.79877927759268308, 0.70294494697955678] #, 1.0073240117407409, 1.0083464927218919]
# data 2018/syst, IR3
I_IR3 = [1,0.8623167576889911, 0.717160103478011, 0.5754527162977867, 0.42569703937913195] #, 1.0045990227076746, 1.0048864616269044, 1.0048864616269044, 1.0048864616269044]
R_IR3 = [1,0.94698908404131044, 0.88318802939301022, 0.81105584279703025, 0.71884042266321613] #, 1.0032316161321539, 0.99981432468949627, 0.99953570360577271, 0.28418906316747955]


# --------------- start main program ---------------------

fig = plt.figure(figsize=[12, 12])

ax = fig.add_subplot(111)

ax.set_xlabel('I/Iref', fontsize=18)
ax.set_ylabel('V/Vref', fontsize=18)
ax.set_xlim(0.4, 1.05) 
ax.set_ylim(0.6, 1.05)
#ax.invert_xaxis()
ax.set_title("2018/syst", fontsize=18)

polOrder = 2

data, = plt.plot(I_IR1, R_IR1, 'k.')
fitRes = np.polyfit(I_IR1, R_IR1, polOrder)
fit, = plt.plot(I_IR1, np.poly1d(fitRes)(I_IR1), 'g-', lw=1)

data2, = plt.plot(I_IR2, R_IR2, 'k*')
fitRes2 = np.polyfit(I_IR2, R_IR2, polOrder)
fit2, = plt.plot(I_IR2, np.poly1d(fitRes2)(I_IR2), 'r-', lw=1)

data3, = plt.plot(I_IR3, R_IR3, 'k+')
fitRes3 = np.polyfit(I_IR3, R_IR3, polOrder)
fit3, = plt.plot(I_IR3, np.poly1d(fitRes3)(I_IR3), 'b-', lw=1)

plt.legend([data, data2, data3], ['IR1', 'IR2', 'IR3'])


plt.show()
plt.tight_layout()
plt.savefig("CurrentDependence.png", bbox_inches="tight")


I_2018=34.8 # mA
I_CERN=35.5 # mA

r = I_2018/I_CERN
print "r= " + str(r)
print str(np.poly1d(fitRes)(r))
print str(np.poly1d(fitRes2)(r))
print str(np.poly1d(fitRes3)(r))
