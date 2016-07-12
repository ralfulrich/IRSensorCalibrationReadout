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


class XYTable:
    def __init__(self):
        print "Initializing the x/y axis..."
        try:
            axisControl1 = serial.Serial("/dev/ttyACM0")
            axisControl1.baudrate = 9600
            axisControl1.timeout = 0.2

            axisControl2 = serial.Serial("/dev/ttyACM1")
            axisControl2.baudrate = 9600
            axisControl2.timeout = 0.2

            send(axisControl1, "TERM=2") # response with plain text and 'OK'
            send(axisControl2, "TERM=2") # response with plain text and 'OK'

            xyMatching = False
            self.xAxis = None
            self.yAxis = None
            serNum1 = send(axisControl1, "?SERNUM")
            serNum2 = send(axisControl2, "?SERNUM")
            if serNum1 == "14080004":
            	self.xAxis = axisControl1
            elif serNum1 == "14080003":
            	self.yAxis = axisControl1
            if serNum2 == "14080004":
            	self.xAxis = axisControl2
            elif serNum2 == "14080003":
            	self.yAxis = axisControl2
    
            if self.xAxis and self.yAxis: xyMatching = True
            if not xyMatching:
            	print "Could not determine, which cotrol unit to use for the x and y axis! Please ask an expert!"

            if send(self.xAxis, "?ASTAT") == 'I' or send(self.yAxis, "?ASTAT") == 'I':
            	initAxis(self.xAxis)
            	initAxis(self.yAxis)
            elif send(self.xAxis, "?ASTAT") == 'O' or send(self.yAxis, "?ASTAT") == 'O':
            	turnOn(self.xAxis)
            	turnOn(self.yAxis)
        except:
   			print "Axis communication not OK -> FIX!!!"
			raise RuntimeError("Axis not working!")

        print "... done."


    def doReference(self):
        print "Reference scan of xy table..."
        send(self.xAxis, "RVELS1=50000" ) # set ref velocity default = 2500
        send(self.xAxis, "RVELF1=-50000" ) # set ref velocity default = -25000
        send(self.xAxis, "REF1=6") # drive to maximum -> minimum:: set minimum to zero
        send(self.yAxis, "RVELS1=50000" ) # set ref velocity default = 2500
        send(self.yAxis, "RVELF1=-50000" ) # set ref velocity default = -25000
        send(self.yAxis, "REF1=6") # drive to maximum -> minimum:: set minimum to zero
        while send(self.xAxis, "?ASTAT") == 'P' or send(self.yAxis, "?ASTAT") == 'P':# check, if stage is moving or reached target positon
            time.sleep(1)
        print "... done."
        return True

    def turnOff(self):
        print "Turning off the axis..."
        send(self.xAxis, "MOFF1")
        send(self.yAxis, "MOFF1")
        print "... done."

    def move(self, mode, axis, target):
        if axis == "x":
        	if mode == "a":
        		setAbsolute(self.xAxis)
        	if mode == "r":
        		setRelative(self.xAxis)
        	setTargetAndGo(self.xAxis,target)
        if axis == "y":
        	if mode == "a":
        		setAbsolute(self.yAxis)
        	if mode == "r":
        		setRelative(self.yAxis)
        	setTargetAndGo(self.yAxis,target)

    def getCurrentPosition(self):
        return int(send(self.xAxis, "?CNT1")), int(send(self.yAxis, "?CNT1"))
        
