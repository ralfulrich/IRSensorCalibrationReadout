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

from plotDataLib  import plotData


        
if (len(sys.argv)<2):
    print "Please give a valid data file!"
    sys.exit()


filename = str(sys.argv[1])
filepath,filename_w_ext = os.path.split(filename)
filename_wo_ext,file_extension = os.path.splitext(filename_w_ext)
pdfName = filepath + "/" + filename_wo_ext+".pdf"

# sensor name...
title = filename[filename.rfind('/')+12:filename.rfind('/')+17]



plotData(filename, title, pdfName)

