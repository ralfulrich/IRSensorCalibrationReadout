#!/usr/bin/python   

import serial       
import time
import sys

from AxisHelper import *
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

mm = 10000.

isSPOCK = False
xAxis = None
xID = 1
xCAN = "00"
yAxis = None
yID = 1
yCAN = "00"


send(axisControl1, "TERM=2") # response with plain text and 'OK'
serNum1 = send(axisControl1, "?SERNUM")
if serNum1 == "14080004":
	xAxis = axisControl1
elif serNum1 == "14080003":
	yAxis = axisControl1
elif serNum1 == "12070211":
        xAxis = axisControl1
        yAxis = axisControl1
        isSPOCK = True
        yCAN = "01"
        
if (not isSPOCK) :
        axisControl2 = serial.Serial("/dev/ttyACM1")
        axisControl2.baudrate = 9600
        axisControl2.timeout = 0.2

        send(axisControl2, "TERM=2") # response with plain text and 'OK'

        serNum2 = send(axisControl2, "?SERNUM")
        if serNum2 == "14080004":
                xAxis = axisControl2
        elif serNum2 == "14080003":
                yAxis = axisControl2

if not xAxis or not yAxis:
	print "Could not determine, which cotrol unit to use for the x and y axis! Please ask Sebastian!"
	sys.exit()

print "status " + send(xAxis, xCAN+"?ASTAT") + " " + send(xAxis, yCAN+"?ASTAT") 

print send(xAxis, xCAN+"EFREE1")
print send(yAxis, yCAN+"EFREE1")

print "status " + send(xAxis, xCAN+"?ASTAT") + " " + send(xAxis, yCAN+"?ASTAT") 

if send(xAxis, xCAN+"?ASTAT") == 'I' or send(xAxis, yCAN+"?ASTAT") == 'I':
	initAxis(xAxis, xID, xCAN)
	initAxis(yAxis, yID, yCAN)
        doReferenceTravel2D(xAxis,yAxis,xID,yID,xCAN,yCAN)
elif send(xAxis, xCAN+"?ASTAT") == 'O' or send(xAxis, yCAN+"?ASTAT") == 'O':
	turnOn(xAxis, xID,xCAN)
	turnOn(yAxis, yID,yCAN)
        
print "status " + send(xAxis, xCAN+"?ASTAT") + " " + send(xAxis, yCAN+"?ASTAT") 



setAbsolute(xAxis,xID,xCAN)
setAbsolute(yAxis,yID,yCAN)
print "goto target1"
setTargetAndGo2D(xAxis,400*mm, yAxis, 400*mm, xID, yID, xCAN,yCAN)

setRelative(xAxis, xID,xCAN)
setRelative(yAxis, yID,yCAN)

startPositionX = -100000
startPositionY = -100000
print "goto target2"
setTargetAndGo2D(xAxis,startPositionX,yAxis,startPositionY, xID, yID, xCAN,yCAN)

stepLength = 60000
nSteps = 3


print "Will scan", nSteps-1, "steps in each directions with", stepLength/10000., "mm spacing..."

StartTime = time.time()
for i in range(nSteps):
	for j in range(nSteps):
		position = getPosition2D(xAxis,yAxis, xID, yID,xCAN,yCAN)
		# print i,j,position[0]/10000., position[1]/10000.
		moveStep(xAxis,stepLength,xID,xCAN)
	moveStep(xAxis,-nSteps*stepLength,xID,xCAN)
	moveStep(yAxis,stepLength,yID,yCAN)
EndTime = time.time()
print "... done."
print "The scan took", (EndTime-StartTime), "seconds."
setAbsolute(xAxis,xID,xCAN)
setAbsolute(yAxis,yID,yCAN)

#print "Will return to 0|0 now."
#setTargetAndGo2D(xAxis,0,yAxis,0,xID,yID,xCAN,yCAN)

turnOff(xAxis,xID,xCAN)
turnOff(yAxis,yID,yCAN)

print ""
print ""
print "The program finished, exiting now!"

sys.exit()
