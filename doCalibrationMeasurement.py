#!/usr/bin/python   

import serial       
import time
import sys, os

from VC840 import * # VC840 multimeter
from connectionCheck import doConnectionCheck
from AxisHelper import *

######################################################

tableInitialized = False
multiInitialized = False
xyTable = None

while(True):
    print ""
    print ""
    print "--------------------------------------------------------------------------------------------"
    print "Please tell me what you want do do:"
    print "--------------------------------------------------------------------------------------------"
    print "t: check if the device communication is ready (recommended at start)"
    print "i: initialze all devices (mandatory at programm start)"
    print "r: do reference scan of both axis (recommended if the axis controls have been turn off)"
    print "m: manual movements of the axis (used to set start position)"
    print "a: automatic scan of the sensor (details can still be specified)"
    print "q: quit this program"
    print "--------------------------------------------------------------------------------------------"
    print ""

    command = raw_input()

    if command  == "t":
        os.system('clear')
        doConnectionCheck()
        continue

    if command  == "i":
        os.system('clear')
        if tableInitialized and multiInitialized:
            print "Already done!"
        else:
            try:
                xyTable = XYTable()
                tableInitialized = True
            except:
                print "Initialization of xy table didn't work!"
            try:
                vc = VC840()
                vc._read_raw_value()
                multiInitialized = True
            except:
                print "Initialization of the multimeter didn't work!"
        continue

    if command  == "r":
        os.system('clear')
        if not tableInitialized:
            print "Please init the devices first"
        else:
            try:
                if xyTable.doReference():
                    print "Reference scan done!"
                else:
                    print "Reference scan could not be performed, please check connection and init stages again!" 
            except:
                print "Weird error - please try reinitializing!"
        continue

    elif command == "m":
        os.system('clear')
        print "Preparing manual movement..."
        mode = raw_input("abolute or relative? (a/r)")
        target = None
        if mode == "a":
            target = float(raw_input("target in mm:"))
            
        elif mode == "r":
            target = float(raw_input("step in mm:"))
            print target*10000
        else:
            print "unknown mode - maybe you want to quit..."
        continue

    elif command == "q":
        os.system('clear')
        print "Goodbye!"
        print ""
        break

    else:
        os.system('clear')
        print "unknown command, try again!"
        continue

sys.exit()
