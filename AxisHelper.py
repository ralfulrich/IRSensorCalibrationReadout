import serial       
import time
import sys

def send(dev, command): # function for sending commands to the stage
    dev.write(command + "\r")
    time.sleep(0.1)
    return dev.read(1024).strip()

def initAxis(axis):
    send(axis, "INIT1") # initialize the stage
    send(axis, "PVEL1=25000") # set max velocity
    send(axis, "ACC1=100000") # set accerleration

def doReferenceTravel(axis):    
    send(axis, "RVELS1=50000" ) # set ref velocity default = 2500
    send(axis, "RVELF1=-50000" ) # set ref velocity default = -25000
    send(axis, "REF1=6") # drive to maximum -> minimum:: set minimum to zero
    while send(axis, "?ASTAT") == 'P':# check, if stage is moving or reached target positon
        time.sleep(1)

def doReferenceTravel2D(axisA,axisB):    
    send(axisA, "RVELS1=50000" ) # set ref velocity default = 2500
    send(axisA, "RVELF1=-50000" ) # set ref velocity default = -25000
    send(axisA, "REF1=6") # drive to maximum -> minimum:: set minimum to zero
    send(axisB, "RVELS1=50000" ) # set ref velocity default = 2500
    send(axisB, "RVELF1=-50000" ) # set ref velocity default = -25000
    send(axisB, "REF1=6") # drive to maximum -> minimum:: set minimum to zero
    while send(axisA, "?ASTAT") == 'P' or send(axisB, "?ASTAT") == 'P':# check, if stage is moving or reached target positon
        time.sleep(1)

def setTargetAndGo(axis,target):
    send(axis, "PSET1="+str(target)) # set target position
    send(axis, "PGO1")# start positioning the stage
    while send(axis, "?ASTAT") == 'T': # wait till movement is finished
        time.sleep(1)

def setTargetAndGo2D(axisA,targetA,axisB,targetB):
    send(axisA, "PSET1="+str(targetA)) # set target position
    send(axisA, "PGO1")# start positioning the stage
    send(axisB, "PSET1="+str(targetB)) # set target position
    send(axisB, "PGO1")# start positioning the stage
    while send(axisA, "?ASTAT") == 'T' or send(axisB, "?ASTAT") == 'T': # wait till movement is finished
        time.sleep(1)

def setRelative(axis):
    send(axis, "RELAT1")

def setAbsolute(axis):
    send(axis, "ABSOL1")

def moveStep(axis,length):
    send(axis, "PSET1="+str(length)) # set step length
    send(axis, "PGO1")# start positioning the stage
    while send(axis, "?ASTAT") == 'T': # wait till movement is finished
        time.sleep(0.1)

def getPosition2D(axisA,axisB):
    return int(send(axisA, "?CNT1")), int(send(axisB, "?CNT1"))

def getRailStatus(axis):
    print 'Status of axis: ' + send(axis, "?ASTAT") # stage status ausgaben
    print 'Current position: ' + send(axis, "?CNT1") # current position

def turnOff(axis):
    send(axis, "MOFF1")

def turnOn(axis):
    send(axis, "MON1")

def moveAbsolute(axis, target):
	if send(axis, "?MODE") == "RELAT":
		setAbsolute(axis)
	setTargetAndGo(axis,target)

def moveRelative(axis, target):
	if send(axis, "?MODE") == "ABSOL":
		setRelative(axis)
	setTargetAndGo(axis,target)
