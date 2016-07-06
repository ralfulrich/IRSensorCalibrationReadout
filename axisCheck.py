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
    print '>reference travel done'

def setTargetAndGo(axis,target):
    send(usb, "PVEL"+str(axis)+"=" + str(maxVelocity)) # set max velocity
    send(usb, "ACC"+str(axis)+"=" + str(accerleration)) # set accerleration
    send(usb, "PSET"+str(axis)+"="+str(target)) # set target position
    send(usb, "PGO"+str(axis)+"")# start positioning the stage
    while send(usb, "?ASTAT")[1] == 'T': # wait till movement is finished
        time.sleep(1)

def getRailStatus(axis):
    print send(usb, "?ASTAT") # stage status ausgaben
    print send(usb, "?CNT"+str(axis)+"") # current position

def turnOff():
    send(usb, "MOFF")
    print '>axis turnes off'
    print '>bye!'

######################################################
######################################################

usb = serial.Serial("/dev/ttyACM0")
usb.baudrate = 9600
usb.timeout = 0.2

if not len(sys.argv) == 1:
    print 'You need to give the axis number'
    print 'Exiting...'
    return

axis = int(sys.argv[0])

send(usb, "TERM=2") # response with plain text and 'OK'

send(usb, "INIT"+str(axis)) # initialize the stage
print '>initialization of axis ' +str(axis) +' 1 done'

doReferenceTravel(axis)

setTargetAndGo(axis,200000)
print '>reached position at ' + str(int(send(usb, "?CNT1")[1])/10000.) +' mm'

getRailStatus(axis)

turnOff()

return
