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
