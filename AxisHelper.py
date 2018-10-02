import serial       
import time
import sys

def send(dev, command): # function for sending commands to the stage
    dev.write(command + "\r")
    time.sleep(0.05)
    return dev.read(1024).strip()

def initAxis(axis, ID, CAN):
    send(axis, CAN+"INIT"+str(ID)) # initialize the stage
    send(axis, CAN+"PVEL"+str(ID)+"=25000") # set max velocity
    send(axis, CAN+"ACC"+str(ID)+"=100000") # set accerleration

def doReferenceTravel(axis, ID,CAN):    
    send(axis, CAN+"RVELS"+str(ID)+"=50000" ) # set ref velocity default = 2500
    send(axis, CAN+"RVELF"+str(ID)+"=-50000" ) # set ref velocity default = -25000
    send(axis, CAN+"REF"+str(ID)+"=6") # drive to maximum -> minimum:: set minimum to zero
    while send(axis, CAN+"?ASTAT") == 'P':# check, if stage is moving or reached target positon
        time.sleep(1)

def doReferenceTravel2D(axisA,axisB,IDA,IDB,CANA,CANB):
    print "do reference travel"
    send(axisA, CANA+"RVELS"+str(IDA)+"=50000" ) # set ref velocity default = 2500
    send(axisA, CANA+"RVELF"+str(IDA)+"=-50000" ) # set ref velocity default = -25000
    send(axisA, CANA+"REF"+str(IDA)+"=6") # drive to maximum -> minimum:: set minimum to zero
    send(axisB, CANB+"RVELS"+str(IDB)+"=50000" ) # set ref velocity default = 2500
    send(axisB, CANB+"RVELF"+str(IDB)+"=-50000" ) # set ref velocity default = -25000
    send(axisB, CANB+"REF"+str(IDB)+"=6") # drive to maximum -> minimum:: set minimum to zero
    while send(axisA, CANA+"?ASTAT") == 'P' or send(axisB, CANB+"?ASTAT") == 'P':# check, if stage is moving or reached target positon
        time.sleep(1)

def setTargetAndGo(axis,target,ID,CAN):
    send(axis, CAN+"PSET"+str(ID)+"="+str(target)) # set target position
    send(axis, CAN+"PGO"+str(ID))# start positioning the stage
    while send(axis, CAN+"?ASTAT") == 'T': # wait till movement is finished
        time.sleep(0.1)

def setTargetAndGo2D(axisA,targetA,axisB,targetB,IDA,IDB,CANA,CANB):
    send(axisA, CANA+"PSET"+str(IDA)+"="+str(targetA)) # set target position
    send(axisA, CANA+"PGO"+str(IDA))# start positioning the stage
    send(axisB, CANB+"PSET"+str(IDB)+"="+str(targetB)) # set target position
    send(axisB, CANB+"PGO"+str(IDB))# start positioning the stage
    while send(axisA, CANA+"?ASTAT") == 'T' or send(axisB, CANB+"?ASTAT") == 'T': # wait till movement is finished
        time.sleep(1)

def setRelative(axis,ID,CAN):
    send(axis, CAN+"RELAT"+str(ID))

def setAbsolute(axis,ID,CAN):
    send(axis, CAN+"ABSOL"+str(ID))

def moveStep(axis,length,ID,CAN):
    send(axis, CAN+"PSET"+str(ID)+"="+str(length)) # set step length
    send(axis, CAN+"PGO"+str(ID))# start positioning the stage
    while send(axis, CAN+"?ASTAT") == 'T': # wait till movement is finished
        time.sleep(0.1)

def getPosition2D(axisA,axisB,IDA,IDB,CANA,CANB):
    return int(send(axisA, CANA+"?CNT"+str(IDA))), int(send(axisB, CANB+"?CNT"+str(IDB)))

def getRailStatus(axis,ID,CAN):
    print 'Status of axis: ' + send(axis, CAN+"?ASTAT") # stage status ausgaben
    print 'Current position: ' + send(axis, CAN+"?CNT"+str(ID)) # current position

def turnOff(axis,ID,CAN):
    send(axis, CAN+"MOFF"+str(ID))

def turnOn(axis,ID,CAN):
    send(axis, CAN+"MON"+str(ID))

def moveAbsolute(axis, target,ID,CAN):
	if send(axis, CAN+"?MODE") == "RELAT":
		setAbsolute(axis, ID)
	setTargetAndGo(axis,target, ID)

def moveRelative(axis, target, ID,CAN):
	if send(axis, CAN+"?MODE") == "ABSOL":
		setRelative(axis, ID)
	setTargetAndGo(axis,target, ID)


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

            send(axisControl1, CAN+"TERM=2") # response with plain text and 'OK'
            send(axisControl2, CAN+"TERM=2") # response with plain text and 'OK'

            xyMatching = False
            self.xAxis = None
            self.yAxis = None
            serNum1 = send(axisControl1, CAN+"?SERNUM")
            serNum2 = send(axisControl2, CAN+"?SERNUM")
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

            if send(self.xAxis, CAN+"?ASTAT") == 'I' or send(self.yAxis, CAN+"?ASTAT") == 'I':
            	initAxis(self.xAxis)
            	initAxis(self.yAxis)
            elif send(self.xAxis, CAN+"?ASTAT") == 'O' or send(self.yAxis, CAN+"?ASTAT") == 'O':
            	turnOn(self.xAxis)
            	turnOn(self.yAxis)
        except:
   			print "Axis communication not OK -> FIX!!!"
			raise RuntimeError("Axis not working!")

        print "... done."


    def doReference(self):
        print "Reference scan of xy table..."
        print (send(self.xAxis, "00?SMK1"))
        send(self.xAxis, CAN+"RVELS1=2500" ) # set ref velocity default = 2500
        send(self.xAxis, CAN+"RVELF1=-50000" ) # set ref velocity default = -25000
        send(self.xAxis, CAN+"REF1=1") # drive to maximum -> minimum:: set minimum to zero
        while send(self.xAxis, CAN+"?ASTAT") == 'P':# check, if stage is moving or reached target positon
            time.sleep(1)
        print (send(self.xAxis, "01?SMK1"))
        send(self.yAxis, CAN+"RVELS1=2500" ) # set ref velocity default = 2500
        send(self.yAxis, CAN+"RVELF1=-50000" ) # set ref velocity default = -25000
        send(self.yAxis, CAN+"REF1=1") # drive to maximum -> minimum:: set minimum to zero
        while send(self.yAxis, CAN+"?ASTAT") == 'P':# check, if stage is moving or reached target positon
            time.sleep(1)
        print "... done."
        return True

    def turnOff(self):
        print "Turning off the axis..."
        send(self.xAxis, CAN+"MOFF1")
        send(self.yAxis, CAN+"MOFF1")
        print "... done."

    def move(self, mode, axis, target):
        if axis == "x":
            #default is absolute, so set first to relative
        	if mode == "r":
        		setRelative(self.xAxis)
            # go
        	setTargetAndGo(self.xAxis,target)
            # set back to absolute
        	if mode == "r":
        		setAbsolute(self.xAxis)
        if axis == "y":
        	if mode == "r":
        		setRelative(self.yAxis)
        	setTargetAndGo(self.yAxis,target)
        	if mode == "r":
        		setAbsolute(self.yAxis)

    def getCurrentPosition(self):
        return int(send(self.xAxis, CAN+"?CNT1")), int(send(self.yAxis, CAN+"?CNT1"))
        
