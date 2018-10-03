#!/usr/bin/python   

import serial       
import time
import sys, os

from VC840 import * # VC840 multimeter
from DMM import * # other multimeters
from connectionCheck import doConnectionCheck
from AxisHelper import *
from progressbar import *

import smtplib
from email.mime.text import MIMEText

def isInEllipse(x,y,x0,y0,a,b):
    if (x-x0)*(x-x0)/a/a+(y-y0)*(y-y0)/b/b <= 1.:
        return True
    else:
        return False

mm = 10000.


startX = (62.-35)*mm  # this is also the default start
startY = 133.*mm      # this is also the default start

centerX = 62.*mm  
centerY = 133.*mm 
scanningEllipse_x0 = 0.*mm 
scanningEllipse_y0 = 0.*mm 
scanningEllipse_a = 35.*mm
scanningEllipse_b = 70.*mm

######################################################
os.system('clear')
tableInitialized = False
multiInitialized = False

xyTable = None
dmm = [] # digital multimeters

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
                print "Initializing the multimeter(s)..."                
                dmm[0] = VC840("/dev/ttyUSB5")
                dmm[0]._read_raw_value()
                dmm[1] = VC840("/dev/ttyUSB6")
                dmm[1]._read_raw_value()
                dmm[2] = DMM("/dev/ttyUSB2")
                dmm[2].readVoltage('m')
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
                print "The current position is ", pos[0]/mm, "|" ,pos[1]/mm, "mm."
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
                target = float(raw_input("target (absolute) in mm:"))*mm
            elif mode == "r":
                target = float(raw_input("step (relative) in mm:"))*mm
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
        
        sendEmail = False
        receiver = ""
        if raw_input("Do you want to get an email notification when the scan is done? (y/n) ") == "y":
            sendEmail = True
            receiver= raw_input("Please enter your email address: ")
        
        if not raw_input("The sensor should be centered infront of the target before the scan starts. Is this already the case? (y/n) ") == "y":
            if raw_input("Do you want to go to the standard starting position? (y/n) ") == "y":
                xyTable.move("a","x",int(centerX))
                xyTable.move("a","y",int(centerY))
            else:
                print "Do you know what you are doing? Please think first - I will quit now..."
                continue

        if not raw_input("This scan will be done in the y-minus direction. Is this ok? (y/n) ") == "y":
            print "quitting..."
            continue
        
        print "Preparing sensor scan..."

        sensorIDlist = []
        sensorXlist = []
        
        while True:
            sensorIDs = raw_input("sensor ID(s) (e.g. 'IR766,IRxxx,...'): ")
            sensorXs = raw_input("sensor x-position(s) in mm [30,32,34]: ") or "30,32,34" 

            sensorIDlist = sensorIDs.split(',')
            sensorXlist = sensorXs.split(',')

            if (len(sensorIDs) == len(sensorXlist)):
                break;

            print ("your input does not fit! ID-list: " + str(sensorIDlist) + " and X-list: " + str(sensorXlist))
            print ("try again")
            
        mode = raw_input("automatic or manual setup of the scan parameters? (a/m): ")        
        
        scanRangeX= 0.*mm
        scanRangeY= 0.*mm
        stepsize = 0.*mm
        initialOffset= 0.*mm
        xDirection = 1
        
        if mode == "a":
            scanRangeX= 70.*mm
            scanRangeY= 70.*mm
            stepsize = 1.*mm
            initialOffset = 4.*mm
            
        else:
            scanRangeX= float(raw_input("total scanning range in mm: ")) * mm
            scanRangeY= scanRangeX
            stepsize = float(raw_input("scanning stepsize in mm: ")) * mm
            initialOffset = float(raw_input("initial minimal distance to the beampipe in mm: ")) * mm
            
        nStepsX = int(scanRangeX/stepsize) + 1
        nStepsY = int(scanRangeY/stepsize) + 1
        startX = centerX - scanRangeX / 2


        print "Moving to start position..."
        try:
            #centralPosition = xyTable.getCurrentPosition()
            xyTable.move("a", "x", startX)
            xyTable.move("a", "y", startY)
            startPosition = xyTable.getCurrentPosition()
        except:
            print "Are you sure the xy table is well initialized?!"
            print "quitting..."
            continue

        if not raw_input("You can now cover the setup. Should I start the scan? (y/n) ") == "y":
            print "quitting..."
            continue

        # create output files
        outputFileList = []
        for iSensor in range(len(sensorIDlist)):
            sensorID = sensorIDlist[iSensor]
            sensorX = float(sensorXlist[iSensor])
            while True:
                version = 1
                filename = "../data/sensorScan_"+str(sensorID)+"_scanRange"+str(scanRangeY)+"_stepSize"+str(stepsize)+"_initialOffset"+str(initialOffset)+"_"+str(version)+".dat"
                if os.path.exists(filename):
                    version += 1
                    #  print "File already exists! Using", filename+"_"+str(version)+".dat", "instead."
                    continue
                print ("Saving sensor " + sensorID + " measurement to file " + filename)

                outputFile = open(filename, 'w' ,1)
                outputFile.write("# Sensor scan measurement of Sensor "+str(sensorID)+"\n")
                outputFile.write("# scanRangeX {:6.2f} mm; scanRangeY {:6.2f} mm; stepSize {:6.2f} mm; initialOffset {:6.2f} mm; sensorX {:6.2f} mm; start position at (x|y)=({:6.2f}|{:6.2f}) mm\n".format(scanRangeX/mm,scanRangeY/mm,stepsize/mm,initialOffset/mm,sensorX,startPosition[0]/mm,startPosition[1]/mm))
                outputFile.write("# iStep, Pos x, Pos y, nMeas, Meas1 ... MeasN\n")

                outputFileList.append(outputFile)
                break
                

        # calulate positions where to measure
        # if automatic eliplic, else square
        # i: y, j:x
        
        scanPositions = []
        for i in range(nStepsX):
            for j in range(nStepsY):
                posX = startPosition[0] + j*stepsize
                posY = startPosition[1] - i*stepsize
                if mode=="a":
                    if (isInEllipse(posX,posY,centerX,centerY,scanningEllipse_a,scanningEllipse_b)):
                        scanPositions.append([posX, posY])
                else:
                    scanPositions.append([posX, posY])

        # start scan
        print "Will scan", len(scanPositions), "positions with", stepsize/mm, "mm spacing in", ("automatic" if mode=="a" else "manual square"), "mode:"
        StartTime = time.time()

        try:
            print ""

            pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()], maxval=len(scanPositions)).start()
            progress = 0

            for pos in scanPositions:
                progress +=1
                xyTable.move("a","x",pos[0])
                xyTable.move("a","y",pos[1])
                position = xyTable.getCurrentPosition()

                # write to output file
                for iFile in range(len(outputFileList)):
                    
                    outputFile = outputFileList[iFile]
                    voltage = dmm[iFile].readStable(5) # 5 measurements
                    
                    outputFile.write("{:6d} {:6d} {:7.2f} {:7.2f} {:3d}".format(progress-1, progress-1,position[0]/mm,position[1]/mm,len(voltage)))
                    for n in range(len(voltage)):
                        outputFile.write(" {:12.2f}".format(voltage[n]))
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

        for outputFile in outputFileList:
            outputFile.write("# END: scan time was  "+str(EndTime-StartTime)+"  seconds")
            outputFile.close()

        email = "The scan of the sensor " + str(sensorID) + " was successfully completed!\n"
        email += "The scan took " + str((EndTime-StartTime)) + " seconds.\n"
        email += "You can now make the next scan.\n"
        msg = MIMEText(email)

        if receiver != "":
            msg['Subject'] = 'IR sensor scan completed'
            msg['From'] = "sebastian.baur@kit.edu"
            msg['To'] = receiver+", sebastian.baur@kit.edu"

            s = smtplib.SMTP('smtp.kit.edu',25)
            s.sendmail("CASTORgroup@kit.edu", [receiver,"sebastian.baur@kit.edu"], msg.as_string())
            s.quit()

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
