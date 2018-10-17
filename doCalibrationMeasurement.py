#!/usr/bin/python   

import serial       
import time
import sys, os

dummyRun = False # no connection to ANY HARDWARE !!!!

from VC840 import * # VC840 multimeter
from DMM import * # other multimeters
from Keithley2750 import *
from connectionCheck import doConnectionCheck
from AxisHelper import *
from progressbar import *

import smtplib
from email.mime.text import MIMEText

def isInEllipse(x, y, x0, y0, a, b):
    if (x-x0)**2/a**2 + (y-y0)**2/b**2 <= 1.:
        return True
    else:
        return False

mm = 10000.

# these six numbers are from Sebastians setup and will be overwritte below
startX = (62.-35)*mm  # this is also the default start
startY = 133.*mm      # this is also the default start
centerX = 62.*mm  
centerY = 133.*mm
xDirection = 1
yDirection = -1

startY = 0. # SPOCK
centerY = 0. # SPOCK
yDirection = 1 # SPOCK

scanningEllipse_a = 35.*mm
scanningEllipse_b = 70.*mm

######################################################
os.system('clear')
tableInitialized = False
multiInitialized = False

xyTable = None
dmm = [] # digital multimeters
channel = []
k2750 = None
vc840 = None
u1272a = None

readVoltage = None

while(True):
    print ""
    print ""
    print "--------------------------------------------------------------------------------------------"
    print "Please tell me what you want do do:"
    print "--------------------------------------------------------------------------------------------"
    print "test/t: check if the device communication is ready (recommended at start)"
    print "init/i: initialze all devices (mandatory at programm start or if axis are off)"
    print "ref/r: do reference scan of both axis (recommended if the axis controls have been turned off)"
    print "pos/p: print current position of the xy table"
    print "move/m: manual movements of the axis (used to set start position)"
    print "pre-scan/P: 1D move and print readings"
    print "scan/s: scan of the sensor (details can still be specified)"
    print "off/o: turn off both axis (usefull if you make a break)"
    print "keithley/k: use keithley to measure voltage"
    print "agilent/a: use Agilent to measure voltage"
    print "quit/q: quit this program"
    print "--------------------------------------------------------------------------------------------"
    print ""

    command = raw_input()

    if command  == "test" or command  == "t":
        os.system('clear')
        doConnectionCheck()
        continue

    elif command  == "init" or command == "i":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        if tableInitialized and multiInitialized:
            print "Already done!"
        else:
            try:
                print ".Initialze the xy table..."
                xyTable = XYTable(isDummy=dummyRun)
                print ".done"
                tableInitialized = True
            except:
                print ".Initialization of xy table didn't work!"
            try:
                print ".Initializing the multimeter(s)..."
                k2750 =  Keithley2750(port="/dev/ttyUSB?", isDummy=dummyRun)
                k2750_port = k2750.getPort()
                #k2750 =  Keithley2750(port="/dev/ttyUSB6", isDummy=dummyRun)
                #k2750 =  Keithley2750(port="/dev/ttyUSB1", isDummy=dummyRun)
                #dmm.append(k2750)
                channel.append("@101")
                channel.append("@102")
                channel.append("@103")
                #vc840 = VC840("/dev/ttyUSB5", isDummy=dummyRun)                
                vc840 = VC840(port="/dev/ttyUSB?", isDummy=dummyRun)
                vc840_port = vc840.getPort()
                #vc840 = VC840("/dev/ttyUSB0", isDummy=dummyRun)
                
                #u1272a = DMM(port="/dev/ttyUSB10")
                u1272a = DMM(port="/dev/ttyUSB?")
                u1272a_port = u1272a.getPort()

                u1272a = DMM(port=u1272a_port)
                vc840 = VC840(port=vc840_port)
                k2750 = Keithley2750(port=k2750_port)
                
                readVoltage = u1272a
                
                multiInitialized = True
                print "... done."
            except:
                print ".Initialization of the multimeter didn't work!"
        continue


    elif command == "keithley" or command == "k":
        print ("measure with Keithley")
        readVoltage = k2750

    elif command == "agilent" or command == "a":
        print ("measure with Agilent")
        readVoltage = u1272a
    
    elif command  == "ref" or command == "r":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
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
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        if not tableInitialized:
            print "Please init the devices first"
        else:
            try:
                pos=xyTable.getCurrentPosition()
                print "The current position is ", pos[0]/mm, "|" , pos[1]/mm, "mm."
            except:
                print "Weird error - please try reinitializing!"
        continue

    elif command == "move" or command == "m":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        print "Preparing manual movement..."
        while(True):
            axis = "u"
            while (axis!="x" and axis!="y" and axis!="q"):
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
            xyTable.move(mode, axis, target)
        continue

    # -----------------------------------------------------------------------------
    elif command == "pre-scan" or command == "P":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        print "Preparing manual movement..."
        ofile = open("pre-scan.dat", "w")
        ofile.write("# pos/mm v1/mV v2/mV v3/mV \n")        
        while(True):
            axis = "u"
            while (axis!="x" and axis!="y" and axis!="q"):
                axis = raw_input("x or y axis? (x/y, q to quit)")
            if axis == "q":
                print "quit..."      
                break

            mode = "a"
            start = float(raw_input("start pos (absolute) in mm:"))*mm
            end = float(raw_input("end pos (absolute) in mm:"))*mm
            nstep = int(raw_input("number of steps:"))
            for istep in range(nstep):
                target = start + (end-start)/(nstep-1) * istep 
                xyTable.move(mode,axis,target)
                k2750.connectChannel(channel[0])
                v1 = readVoltage.readStable(nMeas=1, accuracy=0.025) 
                k2750.connectChannel(channel[1])
                v2 = readVoltage.readStable(nMeas=1, accuracy=0.025) 
                k2750.connectChannel(channel[2])
                v3 = readVoltage.readStable(nMeas=1, accuracy=0.025) 
                print (" pos: %5d mm, v1=%6.2f mV, v2=%6.2f mV, v3=%6.2f mV" % (target/mm, v1[0], v2[0], v3[0]))
                ofile.write( "%5d %5d %6.2f %6.2f %6.2f \n" % (istep, target/mm, v1[0], v2[0], v3[0]))
                ofile.flush()
            continue
        
        ofile.close()

        
    # -----------------------------------------------------------------------------------
    elif command == "scan" or command == "s":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        print ""
        
        sendEmail = False
        receiver = ""
        if (raw_input("Do you want to get an email notification when the scan is done? (y/n) [y] ") or "y") == "y":
            sendEmail = True
            receiver= raw_input("Please enter your email address [ralf.ulrich@kit.edu]: ") or "ralf.ulrich@kit.edu"
        
        # if not raw_input("The sensor should be centered infront of the target before the scan starts. Is this already the case? (y/n) ") == "y":
        #     if raw_input("Do you want to go to the standard starting position? (y/n) ") == "y":
        #         xyTable.move("a","x",int(centerX))
        #         xyTable.move("a","y",int(centerY))
        #     else:
        #         print "Do you know what you are doing? Please think first - I will quit now..."
        #         continue
        
        #if not raw_input("This scan will be done in the y-minus direction. Is this ok? (y/n) ") == "y":
        #    print "quitting..."
        #    continue
        
        print "Preparing sensor scan..."

        sensorIDlist = []
        sensorXlist = []
        
        while True:
            sensorIDs = raw_input("sensor ID(s) (e.g. 'IR766,IRxxx,...')  [IR1,IR2,IR3]: ") or "IR1,IR2,IR3"
            sensorXs = raw_input("sensor x-position(s) in mm [155,195.5,236.5]: ") or "155,195.5,236.5" 

            sensorIDlist = sensorIDs.split(',')
            sensorXlist = [(float(v)*mm) for v in sensorXs.split(',')]

            if (len(sensorIDlist) == len(sensorXlist)):
                break;

            print ("your input does not fit! ID-list: " + str(sensorIDlist) + " and X-list: " + str(sensorXlist))
            print ("try again")

        stepsize = 0.*mm
        stepsize = float(raw_input("scanning stepsize in mm [2]: ") or "2") * mm            
        mode = raw_input("automatic or manual setup of the scan parameters? (a/m) [a]: ") or "a" 
        
        scanRangeX= 0.*mm
        scanRangeY= 0.*mm
        initialOffset= 0.*mm
        xDirection = 1
        
        if mode == "a":
            scanRangeX = max(sensorXlist) - min(sensorXlist) + 70.*mm # 70mm, but in front of every sensor!
            centerX = sum(sensorXlist)/len(sensorXlist) 
            scanRangeY= 70.*mm
            #stepsize = 1.*mm
            initialOffset = 4.*mm
            
        else:
            scanRangeX= float(raw_input("total scanning range in mm: ")) * mm
            scanRangeY= scanRangeX
            #stepsize = float(raw_input("scanning stepsize in mm: ")) * mm
            initialOffset = float(raw_input("initial minimal distance to the beampipe in mm: ")) * mm
            
        nStepsX = int(scanRangeX/stepsize) + 1
        nStepsY = int(scanRangeY/stepsize) + 1
        startX = centerX - scanRangeX/2

        print ".centerX=" + str(centerX/mm) + " miX=" + str(min(sensorXlist)/mm) + " maxX=" + str(max(sensorXlist)/mm)
        print ".startX=" + str(startX/mm) + " startY=" + str(startY/mm) + " rangeX=" + str(scanRangeX/mm)
        print ".nX=" + str(nStepsX) + " nY=" + str(nStepsY)
        print ".Moving to start position..."
        
        xyTable.move2D("a", startX, startY)
        startPosition = xyTable.getCurrentPosition() # -> startX, startY
        
        if not (raw_input("Should I start the scan? (y/n) [y] ") or "y") == "y":
            print "quitting..."
            continue

        
        # current and voltage monitor        
        Iin = None
        Vin = None
        Temp = None
        if (dummyRun):
            Iin = 0.0
            Vin = 0.0
            Temp = 0.0
        else:
            while (Iin == None):
                Iin = vc840.readCurrent("m")
                print (".Iin=" + str(Iin) + " mA")
                
            k2750.connectChannel("@104")
            while (Vin == None):
                Vin = readVoltage.readStable(nMeas=1, accuracy=0.05)[0]
                print (".Vin=" + str(Vin) + " mV")

            Temp = u1272a.readTemperature()
            print (".Temperature=" + str(Temp))
        
        # create output files
        outputFileList = []
        for iSensor in range(len(sensorIDlist)):
            
            sensorID = sensorIDlist[iSensor]
            sensorX = sensorXlist[iSensor]
            version = 1 # file version
            while True:
                filename = "../data/sensorScan_"+str(sensorID)+"_scanRange"+str(scanRangeY)+"_stepSize"+str(stepsize)+"_initialOffset"+str(initialOffset)+"_"+str(version)+".dat"
                if os.path.exists(filename):
                    version += 1
                    #  print "File already exists! Using", filename+"_"+str(version)+".dat", "instead."
                    continue
                print ("Saving sensor " + sensorID + " measurement to file " + filename)
                
                if (not dummyRun) :
                    outputFile = open(filename, 'w' ,1)
                    outputFile.write("# Sensor scan measurement of Sensor "+str(sensorID)+"\n")
                    outputFile.write("# Iin= %8.2f mA ,  Vin= %8.2f mV, T= %8.2f C \n" % (Iin, Vin, Temp))
                    outputFile.write("# scanRangeX {:6.2f} mm; scanRangeY {:6.2f} mm; stepSize {:6.2f} mm; initialOffset {:6.2f} mm; sensorX {:6.2f} mm; start position at (x|y)=({:6.2f}|{:6.2f}) mm\n".format(scanRangeX/mm,scanRangeY/mm,stepsize/mm,initialOffset/mm,sensorX/mm,startPosition[0]/mm,startPosition[1]/mm))
                    outputFile.write("# iStep, iStep, Pos x, Pos y, nMeas, Meas1 ... MeasN\n")

                    outputFileList.append(outputFile)
                break
                

        # calulate positions where to measure
        # if automatic eliplic, else square
        # i: y, j:x
        
        scanPositions = []        
        nRangeCut = 0
        maxRangeCut = 0
        for i in range(nStepsX):
            for j in range(nStepsY):
                posX = startX + xDirection * i*stepsize
                posY = startY + yDirection * j*stepsize

                if (posX>=280*mm) : # out of range in SPOCK
                    nRangeCut += 1
                    maxRangeCut = max(maxRangeCut, posX)
                    continue
                
                if mode=="a":
                    # check if in any ellipse before sensor
                    sensList = []
                    for iSensor in range(len(sensorXlist)):
                        sensorX = sensorXlist[iSensor]
                        # print (" %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f \n" % (posX, posY, sensorX, centerY, scanningEllipse_a, scanningEllipse_b))
                        if (isInEllipse(posX, posY, sensorX, centerY, scanningEllipse_a, scanningEllipse_b)):
                            sensList.append(iSensor)
                    if (len(sensList)>0):
                        scanPositions.append([posX, posY, sensList])

                else:
                    scanPositions.append([posX, posY, []])

        if (nRangeCut>0):
            print (".nRangeCut=" + str(nRangeCut) + " maxRangeCut=" + str(maxRangeCut))

        doDumpPos = False
        if (doDumpPos) :
            dumpPos = open("scanPos.dat", "w")
            for _pos in scanPositions:
                is1 = "0"
                is2 = "0"
                is3 = "0"
                if (0 in _pos[2]): is1 = "1"
                if (1 in _pos[2]): is2 = "1"
                if (2 in _pos[2]): is3 = "1"
                dumpPos.write(str(_pos[0]) + " " + str(_pos[1]) + " " + is1 + " " + is2 + " " + is3 + "\n")
                print (str(_pos[0]) + " " + str(_pos[1]) + " " + is1 + " " + is2 + " " + is3)

            dumpPos.close();
            
            
        # start scan
        print ".Will scan", len(scanPositions), "positions with", stepsize/mm, "mm spacing in", ("automatic" if mode=="a" else "manual square"), "mode:"
        StartTime = time.time()

        print "."

        pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()], maxval=len(scanPositions)).start()
        progress = 0

        for pos in scanPositions:
            progress +=1
            xyTable.move2D("a", pos[0], pos[1])
            position = xyTable.getCurrentPosition()

            # write to output file
            for iSensor in range(len(sensorXlist)):

                if (not dummyRun):
                    outputFile = outputFileList[iSensor]
                    doMeasurement = True
                    if doMeasurement and (iSensor in pos[2]):
                        k2750.connectChannel(channel[iSensor])
                        voltage = readVoltage.readStable(nMeas=1, accuracy=0.025) # 5 measurements ? ... 1

                        outputFile.write("{:6d} {:6d} {:7.2f} {:7.2f} {:3d}".format(progress-1, progress-1,position[0]/mm,position[1]/mm,len(voltage)))
                        for n in range(len(voltage)):
                            outputFile.write(" {:12.2f}".format(voltage[n]))
                        outputFile.write("\n")
                        outputFile.flush()

            pbar.update(progress)

        pbar.finish()

        
        EndTime = time.time()
        print "... done."
        print ".The scan took", (EndTime-StartTime), "seconds."
        #print "Will return to 0|0 now."
        #xyTable.move("a","x",0)
        #xyTable.move("a","y",0)

        if (not dummyRun) :
            for outputFile in outputFileList:
                outputFile.write("# END: scan time was  "+str(EndTime-StartTime)+"  seconds\n")
                outputFile.close()
        
            email = "The scan of the sensor " + str(sensorID) + " was successfully completed!\n"
            email += "The scan took " + str((EndTime-StartTime)) + " seconds.\n"
            email += "You can now make the next scan.\n"
            msg = MIMEText(email)

            if receiver != "":
                msg['Subject'] = 'IR sensor scan completed'
                msg['From'] = "ralf.ulrich@kit.edu"
                msg['To'] = receiver # +", ralf.ulrich@kit.edu"

                s = smtplib.SMTP('smtp.kit.edu',25)
                s.sendmail("CASTORgroup@kit.edu", [receiver,"ralf.ulrich@kit.edu"], msg.as_string())
                s.quit()

        continue


    elif command == "off" or command == "o":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        try:
            xyTable.turnOff()
            tableInitialized = False
        except:
            print "Weird error - please try reinitializing!"
        continue

    elif command == "quit" or command == "q":
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        print "Goodbye!"
        print ""
        break

    else:
        #os.system('clear')
        print("-----------------------------------------------------------\n")
        print "unknown command, try again!"
        continue

sys.exit()
