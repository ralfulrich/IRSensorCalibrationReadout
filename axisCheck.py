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

def doReferenceTravel(axis):    
    send(axisControl, "RVELS"+str(axis)+"=2500" ) # set ref velocity default = 2500
    send(axisControl, "RVELF"+str(axis)+"=-25000" ) # set ref velocity default = -25000
    send(axisControl, "REF"+str(axis)+"=6") # drive to maximum -> minimum:: set minimum to zero
    while send(axisControl, "?ASTAT") == ('?ASTAT', 'P'):# check, if stage is moving or reached target positon
        time.sleep(1)
    print 'Reference travel done'

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

if not len(sys.argv) == 2:
    print 'You need to give the axis number'
    print 'Exiting...'
    exit

axis = int(sys.argv[1])

send(axisControl, "TERM=2") # response with plain text and 'OK'

send(axisControl, "INIT"+str(axis)) # initialize the stage
print 'Initialization of axis ' +str(axis) +' done'

doReferenceTravel(axis)

setTargetAndGo(axis,300000)

getRailStatus(axis)

turnOff(axis)

getRailStatus(axis)

exit
