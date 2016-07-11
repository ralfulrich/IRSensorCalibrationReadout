#!/usr/bin/python   

import serial       
import time
import sys

############################################################################
# axis parameters
velocity = 25000
accerleration = 100000
############################################################################
# helper functions

def send(dev, command): # function for sending commands to the stage
    dev.write(command + "\r")
    time.sleep(0.1)
    return dev.read(1024).strip()

def initAxis(axis):
    send(axis, "INIT1") # initialize the stage
    send(axis, "PVEL1=" + str(velocity)) # set max velocity
    send(axis, "ACC1=" + str(accerleration)) # set accerleration

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

######################################################

print ""
print "Welcome to a first pattern movement test!"
print "Make sure, that you have run the connection test before!"
while(True):
	if raw_input("Did you do so? (y/n)") == "n":
		print "Please do this first!"
		sys.exit()
	elif raw_input("Did you do so? (y/n)") == "y":
		print "Great, let's continue!"
		break
	else:
		print "I did not understand your answer, try again!"

print ""
print ""
print "Initializing the x/y axis..."

axisControl1 = serial.Serial("/dev/ttyACM0")
axisControl1.baudrate = 9600
axisControl1.timeout = 0.2

axisControl2 = serial.Serial("/dev/ttyACM1")
axisControl2.baudrate = 9600
axisControl2.timeout = 0.2

send(axisControl1, "TERM=2") # response with plain text and 'OK'
send(axisControl2, "TERM=2") # response with plain text and 'OK'

xyMatching = False
xAxis = None
yAxis = None
serNum1 = send(axisControl1, "?SERNUM")
serNum2 = send(axisControl2, "?SERNUM")
if serNum1 == "14080004":
	xAxis = axisControl1
elif serNum1 == "14080003":
	yAxis = axisControl1
if serNum2 == "14080004":
	xAxis = axisControl2
elif serNum2 == "14080003":
	yAxis = axisControl2

if xAxis and yAxis: xyMatching = True
if not xyMatching:
	print "Could not determine, which cotrol unit to use for the x and y axis! Please ask Sebastian!"
	sys.exit()

if send(axisControl1, "?ASTAT") == 'I' or send(axisControl1, "?ASTAT") == 'I':

	initAxis(xAxis)
	initAxis(yAxis)
	doReferenceTravel2D(xAxis,yAxis)
elif send(axisControl1, "?ASTAT") == 'O' or send(axisControl1, "?ASTAT") == 'O':
	turnOn(xAxis)
	turnOn(yAxis)

startPositionX = 200000
startPositionY = 200000

setTargetAndGo2D(xAxis,startPositionX,yAxis,startPositionY)

setRelative(xAxis)
setRelative(yAxis)

stepLength = 20000
nSteps = 2

print "Will scan", nSteps-1, "steps in each directions with", stepLength/10000., "mm spacing..."

StartTime = time.time()
for i in range(nSteps):
	for j in range(nSteps):
		position = getPosition2D(xAxis,yAxis)
		print i,j,position[0]/10000., position[1]/10000.
		moveStep(xAxis,stepLength)
	moveStep(xAxis,-nSteps*stepLength)
	moveStep(yAxis,stepLength)
EndTime = time.time()
print "... done."
print "The scan took", (EndTime-StartTime), "seconds."
print "Will return to 0|0 now."

setAbsolute(xAxis)
setAbsolute(yAxis)

setTargetAndGo2D(xAxis,0,yAxis,0)

turnOff(xAxis)
turnOff(yAxis)

print ""
print ""
print "The program finished, exiting now!"

sys.exit()
