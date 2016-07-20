#!/usr/bin/python   

import serial       
import time
import sys, os

from VC840 import * # VC840 multimeter
from connectionCheck import doConnectionCheck
from AxisHelper import *
from progressbar import *


def isInEllipse(x,y,x0,y0,a,b):
    if (x-x0)*(x-x0)/a/a+(y-y0)*(y-y0)/b/b <= 1.:
        return True
    else:
        return False

scanningEllipse_x0 = 62. # this is also the default start
scanningEllipse_y0 = 133. # this is also the default start
scanningEllipse_a = 35.
scanningEllipse_b = 70.

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
    print "scan: scan of the sensor (details can still be specified)"
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
            if raw_input("Do you want to go to the standard starting position? (y/n) ") == "y":
                xyTable.move("a","x",int(scanningEllipse_x0*10000))
                xyTable.move("a","y",int(scanningEllipse_y0*10000))
            else:
                print "Do you know what you are doing? Please think first - I will quit now..."
                continue

        if not raw_input("This scan will be done in the y-minus direction. Is this ok? (y/n) ") == "y":
            print "quitting..."
            continue

        print "Preparing sensor scan..."
        sensorID = raw_input("sensor ID (e.g. 'IR766'): ")
        mode = raw_input("automatic or manual setup of the scan parameters? (a/m): ")

        scanRange= 0.
        stepsize = 0.
        initialOffset= 0.
        xDirection = 1

        if mode == "a":
            scanRange= 70.
            stepsize = 1.
            initialOffset = 4.

        else:
            scanRange= float(raw_input("total scanning range in mm: "))
            stepsize = float(raw_input("scanning stepsize in mm: "))
            initialOffset = float(raw_input("initial minimal distance to the beampipe in mm: "))

        nSteps = int(scanRange/stepsize)+1

        filename = "../data/sensorScan_"+str(sensorID)+"_scanRange"+str(scanRange)+"_stepSize"+str(stepsize)+"_initialOffset"+str(initialOffset)
        version = 1
        print "Saving measurement to ",filename+"_"+str(version)+".dat"
        while os.path.exists(filename+"_"+str(version)+".dat"):
            version += 1
            print "File already exists! Using", filename+"_"+str(version)+".dat", "instead."

        centralPosition=[0,0]

        print "Moving to start position..."
        try:
            centralPosition = xyTable.getCurrentPosition()
            xyTable.move("r","x",-1*xDirection*int(nSteps/2)*stepsize*10000)
            startPosition = xyTable.getCurrentPosition()
        except:
            print "Are you sure the xy table is well initialized?!"
            print "quitting..."
            continue

        # calulate positions where to measure
        # if automatic eliplic, else square
        # i: y, j:x

        scanPositions = []
        for i in range(nSteps):
            for j in range(nSteps):
                if mode=="a":
                    if isInEllipse(startPosition[0]/10000+j*stepsize,startPosition[1]/10000+i*stepsize,scanningEllipse_x0,scanningEllipse_y0,scanningEllipse_a,scanningEllipse_b):
                        scanPositions.append([startPosition[0]+j*stepsize*10000,startPosition[1]+i*stepsize*10000])
                else:
                    scanPositions.append([startPosition[0]+j*stepsize*10000,startPosition[1]+i*stepsize*10000])       

        # start scan
        print "Will scan", len(scanPositions), "positions with", stepsize, "mm spacing in", ("automatic" if mode=="a" else "manual square"), "mode:"
        StartTime = time.time()
        outputFile = open(filename+"_"+str(version)+".dat",'w',1)
        outputFile.write("# Sensor scan measurement of Sensor "+str(sensorID)+"\n")
        outputFile.write("# scanRange {:6.2f} mm; stepSize {:6.2f} mm; initialOffset {:6.2f} mm; start position at (x|y)=({:6.2f}|{:6.2f}) mm\n".format(scanRange,stepsize,initialOffset,startPosition[0]/10000,startPosition[1]/10000))
        outputFile.write("# iStep x, iStep y, Pos x, Pos y, nMeas, Meas1 ... MeasN\n")

        try:
            print ""

            pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()], maxval=len(scanPositions)).start()
            progress = 0

            for pos in scanPositions:
                progress +=1
                xyTable.move("a","x",pos[0])
                xyTable.move("a","y",pos[1])
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
                    if (tmp1-tmp2)<(0.01*tmp1):
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
                pbar.update(progress)

            pbar.finish()

        except:
            print "Are you sure the xy table is well initialized?!"
            continue

        EndTime = time.time()
        print "... done."
        print "The scan took", (EndTime-StartTime), "seconds."
        print "Will return to 0|0 now."
        xyTable.move("a","x",0)
        xyTable.move("a","y",0)

        outputFile.write("# END: scan time was  "+str(EndTime)+"  seconds")
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
