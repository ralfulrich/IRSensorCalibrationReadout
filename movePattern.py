#!/usr/bin/python   

import serial       
import time
import sys

############################################################################
############################################################################
velocity = 50000 #150000 #180000
accerleration = 10000 #200000          
############################################################################
############################################################################

axisControl = serial.Serial("/dev/ttyACM0")
axisControl.baudrate = 9600
axisControl.timeout = 0.2

def send(dev, command): # function for sending commands to the stage
    dev.write(command + "\r")
    return command.strip(), dev.read(1024).strip()

def initAxis(axis):
    print "Initialization of Axis " + str(axis) + " ..."
    send(axisControl, "INIT"+str(axis)) # initialize the stage
    print '    ... done'
    print "Do refence scan of Axis " + str(axis) + "..."
    doReferenceTravel(axis)

def doReferenceTravel(axis):    
    send(axisControl, "RVELS"+str(axis)+"=2500" ) # set ref velocity default = 2500
    send(axisControl, "RVELF"+str(axis)+"=-25000" ) # set ref velocity default = -25000
    send(axisControl, "REF"+str(axis)+"=6") # drive to maximum -> minimum:: set minimum to zero
    while send(axisControl, "?ASTAT") == ('?ASTAT', 'P'):# check, if stage is moving or reached target positon
        time.sleep(1)
    print '    ... done'

def setTargetAndGo(axis,target):
    send(axisControl, "PVEL"+str(axis)+"=" + str(velocity)) # set max velocity
    send(axisControl, "ACC"+str(axis)+"=" + str(accerleration)) # set accerleration
    send(axisControl, "PSET"+str(axis)+"="+str(target)) # set target position
    send(axisControl, "PGO"+str(axis)+"")# start positioning the stage
    while send(axisControl, "?ASTAT")[1] == 'T': # wait till movement is finished
        time.sleep(1)
    print 'Reached position at ' + str(int(send(axisControl, "?CNT1")[1])/10000.) +' mm'

def getRailStatus(axis):
    print 'Status of axis ' + str(axis) + ': ' + send(axisControl, "?ASTAT")[1] # stage status ausgaben
    print 'Cuttent position: ' + send(axisControl, "?CNT"+str(axis)+"")[1] # current position

def turnOff(axis):
    print 'Turning of axis ' + str(axis)
    send(axisControl, "MOFF"+str(axis))


######################################################
######################################################

send(axisControl, "TERM=2") # response with plain text and 'OK'

initAxis(1)
initAxis(2)

getRailStatus(axis)

# initial position
setTargetAndGo(1,300000)
setTargetAndGo(2,300000)

getRailStatus(axis)

nStepsX = 10
widthX = 2
nStepsY = 10
widthY = 2

turnOff(1)
turnOff(2)

getRailStatus(1)
getRailStatus(2)

sys.exit
