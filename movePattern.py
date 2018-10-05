#!/usr/bin/python   

import serial       
import time
import sys

from AxisHelper import *
######################################################

print ""
print "Welcome to a first pattern movement test!"
print "Make sure, that you have run the connection test before!"
while(False):
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

mm = 10000.

xyTable = XYTable()

xyTable.doReference() # 2D

xyTable.getRailStatus("x")
xyTable.getRailStatus("y")

#xyTable.setRelative("x")
#xyTable.setRelative("y")
#print "goto target0"
#xyTable.setTargetAndGo2D(-20*mm, 20*mm)

xyTable.setAbsolute("x")
xyTable.setAbsolute("y")
print "goto target1"
xyTable.setTargetAndGo2D(10*mm, 10*mm)

print "goto target2"
xyTable.setTargetAndGo2D(100*mm, 100*mm)


stepLength = 60000
nSteps = 3

print "Will scan", nSteps-1, "steps in each directions with", stepLength/10000., "mm spacing..."

xyTable.setRelative("x")
xyTable.setRelative("y")

StartTime = time.time()
for i in range(nSteps):
	for j in range(nSteps):
		position = xyTable.getCurrentPosition()
		# print i,j,position[0]/10000., position[1]/10000.
		xyTable.move("r", "x", stepLength)
	xyTable.move("r", "x", -nSteps*stepLength)
	xyTable.move("r", "y", stepLength)
EndTime = time.time()
print "... done."
print "The scan took", (EndTime-StartTime), "seconds."

#print "Will return to 0|0 now."
#setTargetAndGo2D(xAxis,0,yAxis,0,xID,yID,xCAN,yCAN)

# xyTable.turnOff()

print ""
print ""
print "The program finished, exiting now!"

sys.exit()
