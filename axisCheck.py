#!/usr/bin/python   

import serial       
import time
import sys

############################################################################
############################################################################
velocity = 100000 #150000 #180000
accerleration = 200000 #200000          
############################################################################
############################################################################

def send(dev, command): # function for sending commands to the stage
    dev.write(command + "\r")
    return command.strip(), dev.read(1024).strip()

def doReferenceTravel(axis):    
    send(usb, "RVELS"+str(axis)+"=-50000" ) # set ref velocity default = 2500
    send(usb, "RVELF"+str(axis)+"=-50000" ) # set ref velocity default = -25000
    send(usb, "REF"+str(axis)+"=6") # drive to maximum -> minimum:: set minimum to zero
    while send(usb, "?ASTAT") == ('?ASTAT', 'P'):# check, if stage is moving or reached target positon
        time.sleep(1)
    print 'Reference travel done'

def setTargetAndGo(axis,target):
    send(usb, "PVEL"+str(axis)+"=" + str(velocity)) # set max velocity
    send(usb, "ACC"+str(axis)+"=" + str(accerleration)) # set accerleration
    send(usb, "PSET"+str(axis)+"="+str(target)) # set target position
    send(usb, "PGO"+str(axis)+"")# start positioning the stage
    while send(usb, "?ASTAT")[1] == 'T': # wait till movement is finished
        time.sleep(1)
    print 'Reached position at ' + str(int(send(usb, "?CNT1")[1])/10000.) +' mm'

def getRailStatus(axis):
    print 'Status of axis ' + str(axis) + ': ' + send(usb, "?ASTAT")[1] # stage status ausgaben
    print 'Cuttent position: ' + send(usb, "?CNT"+str(axis)+"")[1] # current position

def turnOff(axis):
    print 'Turning of axis ' + str(axis)
    send(usb, "MOFF"+str(axis))


######################################################
######################################################

usb = serial.Serial("/dev/ttyACM0")
usb.baudrate = 9600
usb.timeout = 0.2

if not len(sys.argv) == 2:
    print 'You need to give the axis number'
    print 'Exiting...'
    exit

axis = int(sys.argv[1])

send(usb, "TERM=2") # response with plain text and 'OK'

send(usb, "INIT"+str(axis)) # initialize the stage
print 'Initialization of axis ' +str(axis) +' done'

doReferenceTravel(axis)

setTargetAndGo(axis,300000)

getRailStatus(axis)

turnOff(axis)

getRailStatus(axis)

exit
