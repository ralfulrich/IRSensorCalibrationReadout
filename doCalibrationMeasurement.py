#!/usr/bin/python   

import serial       
import time
import sys, os

from VC840 import * # VC840 multimeter
from connectionCheck import doConnectionCheck
from AxisHelper import *
from progressbar import *

######################################################
os.system('clear')
tableInitialized = False
multiInitialized = False

xyTable = None
vc = None

while(True):
    print ""
    print ""
    print "--------------------------------------------------------------------------------------------"
    print "Please tell me what you want do do:"
    print "--------------------------------------------------------------------------------------------"
    print "test: check if the device communication is ready (recommended at start)"
    print "init: initialze all devices (mandatory at programm start or if axis are off)"
    print "ref: do reference scan of both axis (recommended if the axis controls have been turned off)"
    print "pos: print current position of the xy table"
    print "move: manual movements of the axis (used to set start position)"
    print "scan: automatic scan of the sensor (details can still be specified)"
    print "off: turn off both axis (usefull if you make a break)"
    print "quit: quit this program"
    print "--------------------------------------------------------------------------------------------"
    print ""

    command = raw_input()

    if command  == "test" or command  == "t":
        os.system('clear')
        doConnectionCheck()
        continue

    elif command  == "init" or command == "i":
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
                print "Initializing the multimeter..."
                vc = VC840()
                vc._read_raw_value()
                multiInitialized = True
                print "... done."
            except:
                print "Initialization of the multimeter didn't work!"
        continue

    elif command  == "ref" or command == "r":
        os.system('clear')
        if not tableInitialized:
            print "Please init the devices first"
        else:
            try:
                if not xyTable.doReference():
                    print "Reference scan could not be performed, please check connection and init stages again!" 
            except:
                print "Weird error - please try reinitializing!"
        continue

    elif command  == "pos" or command == "p":
        os.system('clear')
        if not tableInitialized:
            print "Please init the devices first"
        else:
            try:
                pos=xyTable.getCurrentPosition()
                print "The current position is ", pos[0]/10000., "|" ,pos[1]/10000., "mm."
            except:
                print "Weird error - please try reinitializing!"
        continue

    elif command == "move" or command == "m":
        os.system('clear')
        print "Preparing manual movement..."
        while(True):
            axis = raw_input("x or y axis? (x/y, q to quit)")
            if axis == "q":
                print "quit..."      
                break

            mode = raw_input("abolute or relative? (a/r, q to quit)")
            target = None
            if mode == "a":
                target = float(raw_input("target in mm:"))*10000
            elif mode == "r":
                target = float(raw_input("step in mm:"))*10000
            elif mode == "q":
                print "quit..."
                break
            else:
                print "unknown mode - maybe you want to quit..."
            try:
                xyTable.move(mode,axis,target)
            except:
                print "Are you sure the xy table is well initialized?!"
        continue

    elif command == "scan" or command == "s":
        os.system('clear')
        print ""

        if not raw_input("The sensor should be centered infront of the target. Is this true? (y/n) ") == "y":
            print "Please adjust the sensor position quitting..."
            continue

        if not raw_input("This scan will be done in the y-minus direction. Is this ok? (y/n) ") == "y":
            print "quitting..."
            continue

        print "Preparing sensor scan..."
        sensorID = raw_input("sensor ID (e.g. 'IR766'): ")
        initialOffset = float(raw_input("initial minimal distance to the beampipe in mm: "))
        scanRange= float(raw_input("total scanning range in mm: "))
        stepsize = float(raw_input("scanning stepsize in mm: "))

        filename = "../data/sensorScan_"+str(sensorID)+"_scanRange"+str(scanRange)+"_stepSize"+str(stepsize)+"_initialOffset"+str(initialOffset)
        version = 1
        print "Saving measurement to ",filename+"_"+str(version)+".dat"
        while os.path.exists(filename+"_"+str(version)+".dat"):
            version += 1
            print "File already exists! Using", filename+"_"+str(version)+".dat", "instead."

        nSteps = int(scanRange/stepsize)+1
        print "Will scan", nSteps, "steps in each direction with", stepsize, "mm spacing..."
        StartPosition = xyTable.getCurrentPosition()
        StartTime = time.time()

        outputFile = open(filename+"_"+str(version)+".dat",'w',0)
        outputFile.write("# Sensor scan measurement of Sensor "+str(sensorID)+"\n")
        outputFile.write("# scanRange {:6.2f} mm; stepSize {:6.2f} mm; initialOffset {:6.2f} mm; start position at (x|y)=({:6.2f}|{:6.2f}) mm\n".format(scanRange,stepsize,initialOffset,StartPosition[0],StartPosition[1]))
        outputFile.write("# iStep x, iStep y, Pos x, Pos y, nMeas, Meas1 ... MeasN\n")

        # add later: ideal start position is 65 | 133 mm with an initial offset of ~4 mm

        xDirection = 1

        try:
            xyTable.move("r","x",-1*xDirection*int(nSteps/2)*stepsize*10000.)

            print ""

            pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()], maxval=(nSteps*nSteps)).start()

            for i in range(nSteps):
                for j in range(nSteps):
                    if not j==0:
                        xyTable.move("r","x",xDirection*stepsize*10000.)
                    position = xyTable.getCurrentPosition()

                    voltage = []

                    # check for stability
                    for m in range(10):
                        tmp1 = None
                        tmp2 = None
                        while tmp1 == None or tmp2==None:
                            tmp1 = vc.readVoltage("m")
                            time.sleep(0.2)
                            tmp2 = vc.readVoltage("m")
                        if (tmp1-tmp2)<(0.05*tmp1):
                            break

                    # save up to 5 values
                    for m in range(5):
                        meas = vc.readVoltage("m")
                        if meas:
                            voltage.append(meas)

                    if len(voltage) < 4:
                        voltage = []
                        for m in range(5):
                            meas = vc.readVoltage("m")
                            if meas:
                                voltage.append(meas)

                    # write to output file
                    outputFile.write("{:3d} {:3d} {:7.2f} {:7.2f} {:3d}".format(j,i,position[0]/10000.,position[1]/10000.,len(voltage)))
                    for n in range(len(voltage)):
                        outputFile.write(" {:12.4f}".format(voltage[n]))
                    outputFile.write("\n")
                    pbar.update(i*(nSteps) + j+1)

                xyTable.move("r","x",-1*xDirection*(nSteps-1)*stepsize*10000.)
                xyTable.move("r","y",-1*stepsize*10000.)

            pbar.finish()
            EndTime = time.time()
            print "... done."
            print "The scan took", (EndTime-StartTime), "seconds."
            print "Will return to 0|0 now."

            xyTable.move("a","x",0)
            xyTable.move("a","y",0)

        except IndentationError:
            print "Are you sure the xy table is well initialized?!"

        outputFile.write("# END")
        outputFile.close()
        continue


    elif command == "off" or command == "o":
        os.system('clear')
        try:
            xyTable.turnOff()
            tableInitialized = False
        except:
            print "Weird error - please try reinitializing!"
        continue

    elif command == "quit" or command == "q":
        os.system('clear')
        print "Goodbye!"
        print ""
        break

    else:
        os.system('clear')
        print "unknown command, try again!"
        continue

sys.exit()
