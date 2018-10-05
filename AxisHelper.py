import serial       
import time
import sys
   
# def doReferenceTravel(axis, ID, CAN):    
#     send(axis, CAN+"RVELS"+str(ID)+"=5000" ) # set ref velocity default = 2500
#     send(axis, CAN+"RVELF"+str(ID)+"=-50000" ) # set ref velocity default = -25000
#     send(axis, CAN+"REF"+str(ID)+"=6") # drive to maximum -> minimum:: set minimum to zero
#     while send(axis, CAN+"?ASTAT") == 'P':# check, if stage is moving or reached target positon
#         time.sleep(1)

# def doReferenceTravel2D(axisA,axisB,IDA,IDB,CANA,CANB):
#     print "do reference travel"
#     print ("limit x: " + send(axisA, "00?SMK1") + ", ref x: " + send(axisA, "00?RMK1")+ ", polref x: " + send(axisA, "00?RPL1"))
#     print ("limit y: " + send(axisB, "01?SMK1") + ", ref y: " + send(axisB, "01?RMK1")+ ", polref y: " + send(axisA, "01?RPL1"))
#     send(axisA, CANA+"RVELS"+str(IDA)+"=2500" ) # set ref velocity default = 2500
#     send(axisA, CANA+"RVELF"+str(IDA)+"=-50000" ) # set ref velocity default = -25000
#     send(axisA, CANA+"REF"+str(IDA)+"=6") # drive to maximum -> minimum:: set minimum to zero
#     send(axisB, CANB+"RVELS"+str(IDB)+"=2500" ) # set ref velocity default = 2500
#     send(axisB, CANB+"RVELF"+str(IDB)+"=-50000" ) # set ref velocity default = -25000
#     send(axisB, CANB+"REF"+str(IDB)+"=6") # drive to maximum -> minimum:: set minimum to zero
#     while send(axisA, CANA+"?ASTAT") == 'P' or send(axisB, CANB+"?ASTAT") == 'P':# check, if stage is moving or reached target positon
#         time.sleep(1)


# def setTargetAndGo2D(axisA,targetA,axisB,targetB,IDA,IDB,CANA,CANB):
#     send(axisA, CANA+"PSET"+str(IDA)+"="+str(targetA)) # set target position
#     send(axisA, CANA+"PGO"+str(IDA))# start positioning the stage
#     send(axisB, CANB+"PSET"+str(IDB)+"="+str(targetB)) # set target position
#     send(axisB, CANB+"PGO"+str(IDB))# start positioning the stage
#     while send(axisA, CANA+"?ASTAT") == 'T' or send(axisB, CANB+"?ASTAT") == 'T': # wait till movement is finished
#         time.sleep(1)

# def moveAbsolute(axis, target,ID,CAN):
# 	if send(axis, CAN+"?MODE") == "RELAT":
# 	    self.setAbsolute(axis, ID)
# 	self.setTargetAndGo(axis,target, ID)
            
# def moveRelative(axis, target, ID,CAN):
# 	if send(axis, CAN+"?MODE") == "ABSOL":
# 	    self.setRelative(axis, ID)
# 	self.setTargetAndGo(axis,target, ID)


class XYTable:
    def __init__(self):
        # each axis is specified by a serial port, an axis ID on the controller, and a controller CAN ID 
        self.xAxis = None
        self.yAxis = None
        self.xID = 1
        self.yID = 1
        self.xCAN = "00"
        self.yCAN = "00"
        print "Initializing the x/y axis..."
        #        try:
        if True:
            port="/dev/ttyACM1"
            print ".connecting to " + port
            axisControl1 = serial.Serial(port)
            axisControl1.baudrate = 9600
            axisControl1.timeout = 0.2

            self.isSPOCK = True

            if not self.isSPOCK:
            
                print ".consider two indipendently connected controllers"
                axisControl2 = serial.Serial("/dev/ttyACM1")
                axisControl2.baudrate = 9600
                axisControl2.timeout = 0.2

                serNum1 = self.send(axisControl1, CAN+"?SERNUM")
                serNum2 = self.send(axisControl2, CAN+"?SERNUM")
                if serNum1 == "14080004":
                    self.xAxis = axisControl1
                elif serNum1 == "14080003":
                    self.yAxis = axisControl1                
                    
                if serNum2 == "14080004":
                    self.xAxis = axisControl2
                elif serNum2 == "14080003":
                    self.yAxis = axisControl2

            else:
                print ".consider two CAN-linked controllers"
                self.yCAN = "01"
                self.xAxis = axisControl1
                self.yAxis = axisControl1
                
            if self.xAxis==None or self.yAxis==None: 
                print "Could not determine, which control unit to use for the x and y axis! Please ask an expert!"
                sys.exit(1)
            
            self.send(self.xAxis, self.xCAN+"TERM=2") # response with plain text and 'OK'
            self.send(self.yAxis, self.yCAN+"TERM=2") # response with plain text and 'OK'

            # check if axes need initialization
            if self.send(self.xAxis, self.xCAN+"?ASTAT") == 'I':
                print ".initialize x"
            	self.initAxis("x")
            if self.send(self.yAxis, self.yCAN+"?ASTAT") == 'I':
                print ".initialize y"
            	self.initAxis("y")

            # check if axes are swtich off
            if self.send(self.xAxis, self.xCAN+"?ASTAT") == 'O':
                print ".turn On x"
            	self.turnOn("x")
            if self.send(self.yAxis, self.yCAN+"?ASTAT") == 'O':
                print ".turn On y"
            	self.turnOn("y")

            # setup axes parameters
            self.setupAxis("x", "0010", "1111")
            self.setupAxis("y", "0010", "1111")
                
            print ".status x: "
            self.getRailStatus("x")
            print ".status y: " 
            self.getRailStatus("y")

            # check if everything is OK
            if self.send(self.xAxis, self.xCAN+"?ASTAT") != 'R' or self.send(self.yAxis, self.yCAN+"?ASTAT") != 'R':
                print "!Not all axes are in READY status. Fix!"
                sys.exit(1)
            
            #except:
   	    #print "Axis communication not OK -> FIX!!!"
	    # raise RuntimeError("Axis not working!")

        print ".initialized"

        
    def getRailStatus(self, axis):
        if (axis=="x"):
            print '.Status of axis: ' + self.send(self.xAxis, self.xCAN+"?ASTAT") # stage status ausgaben
            print '.Current position: ' + self.send(self.xAxis, self.xCAN+"?CNT"+str(self.xID)) # current position
        else:
            print '.Status of axis: ' + self.send(self.yAxis, self.yCAN+"?ASTAT") # stage status ausgaben
            print '.Current position: ' + self.send(self.yAxis, self.yCAN+"?CNT"+str(self.yID)) # current position

        
    def doReference(self):
        print ("Reference scan of XY table...")
        print (".limit x: " + self.send(self.xAxis, self.xCAN+"?SMK1") + ", refmask x: " + self.send(self.xAxis, self.xCAN+"?RMK1")+ ", polref x: " + self.send(self.xAxis, self.xCAN+"?RPL1"))
        statX = self.send(self.xAxis, self.xCAN+"?REFST1")
        if (statX == "1"):
            print (".already calibrated!")
        else:
            self.send(self.xAxis, self.xCAN+"RVELS1=2500" )         # set ref velocity default = 2500
            self.send(self.xAxis, self.xCAN+"RVELF1=-50000" )       # set ref velocity default = -25000
            self.send(self.xAxis, self.xCAN+"REF1=1")               # drive to maximum -> minimum:: set minimum to zero.  WHY NOT MODE 6???

        print (".limit y: " + self.send(self.yAxis, self.yCAN+"?SMK1") + ", refmask y: " + self.send(self.yAxis, self.yCAN+"?RMK1")+ ", polref y: " + self.send(self.yAxis, self.yCAN+"?RPL1"))
        statY = self.send(self.yAxis, self.yCAN+"?REFST1")
        if (statY == "1"):
            print (".already calibrated!")
        else:
            self.send(self.yAxis, self.yCAN+"RVELS1=2500" ) # set ref velocity default = 2500
            self.send(self.yAxis, self.yCAN+"RVELF1=-50000" ) # set ref velocity default = -25000
            self.send(self.yAxis, self.yCAN+"REF1=1") # drive to maximum -> minimum:: set minimum to zero                  WHY NOT MODE 6???
        
        # check, if stage is moving or reached target positon
        self.waitWhile('P')
        self.setOrigin()
        return True

    
    def waitWhile(self, status, wait=1):
        print ('.wait while axes status is ' + status)
        while self.send(self.xAxis, self.xCAN+"?ASTAT") == status or self.send(self.yAxis, self.yCAN+"?ASTAT") == status : 
            time.sleep(wait)
        print (".reached position")

        
    # turn off everything
    def turnOff(self):
        print "Turning off the axis..."
        self.send(self.xAxis, self.xCAN+"MOFF1")
        self.send(self.yAxis, self.yCAN+"MOFF1")
        print ".done"


    # switch on single axis
    def turnOn(self, axis):
        print "Turning on the axis..."
        if (axis=="x"):
            self.send(self.xAxis, self.xCAN+"MON1")
        else:
            self.send(self.yAxis, self.yCAN+"MON1")
        print ".done"
        
        
    def move(self, mode, axis, target):
        #default is absolute, so set first to relative
        if mode == "r":
            self.setRelative(axis)
        else:
            self.setAbsolute(axis)
        # go
        self.setTargetAndGo(axis, target)
        # set back to absolute
        #if mode == "r":
        #   self.setAbsolute(axis)

                        
    def getCurrentPosition(self):
        return int(self.send(self.xAxis, self.xCAN+"?CNT1")), int(self.send(self.yAxis, self.yCAN+"?CNT1"))


    def setOrigin(self):
        self.send(self.xAxis, self.xCAN+"CNT1=0")
        self.send(self.yAxis, self.yCAN+"CNT1=0")

    
    def setTargetAndGo(self, axis, target):
        if (axis=="x"):
            self.send(self.xAxis, self.xCAN+"PSET"+str(self.xID)+"="+str(target)) # set target position
            self.send(self.xAxis, self.xCAN+"PGO"+str(self.xID))# start positioning the stage
            while self.send(self.xAxis, self.xCAN+"?ASTAT") == 'T': # wait till movement is finished
                time.sleep(0.1)
        else:
            self.send(self.yAxis, self.yCAN+"PSET"+str(self.yID)+"="+str(target)) # set target position
            self.send(self.yAxis, self.yCAN+"PGO"+str(self.yID))# start positioning the stage
            while self.send(self.yAxis, self.yCAN+"?ASTAT") == 'T': # wait till movement is finished
                time.sleep(0.1)

                
    def setTargetAndGo2D(self, targetx, targety):
        self.send(self.xAxis, self.xCAN+"PSET"+str(self.xID)+"="+str(targetx)) # set target position
        self.send(self.xAxis, self.xCAN+"PGO"+str(self.xID))# start positioning the stage

        self.send(self.yAxis, self.yCAN+"PSET"+str(self.yID)+"="+str(targety)) # set target position
        self.send(self.yAxis, self.yCAN+"PGO"+str(self.yID))# start positioning the stage

        while self.send(self.xAxis, self.xCAN+"?ASTAT") == 'T': # wait till movement is finished
            time.sleep(0.1)
        while self.send(self.yAxis, self.yCAN+"?ASTAT") == 'T': # wait till movement is finished
            time.sleep(0.1)

                
    def setRelative(self, axis):
        if (axis == "x"):
            self.send(self.xAxis, self.xCAN+"RELAT"+str(self.xID))
        else:
            self.send(self.yAxis, self.yCAN+"RELAT"+str(self.yID))

            
    def setAbsolute(self, axis):
        if (axis == "x"):
            self.send(self.xAxis, self.xCAN+"ABSOL"+str(self.xID))
        else:
            self.send(self.yAxis, self.yCAN+"ABSOL"+str(self.yID))

            
    def initAxis(self, axis):
        if (axis == "x"):
            self.send(self.xAxis, self.xCAN+"INIT"+str(self.xID)) # initialize the stage
        else:
            self.send(self.yAxis, self.yCAN+"INIT"+str(self.yID)) # initialize the stage

        
    def setupAxis(self, axis, refmask="0001", refmask2="1110"): # RMK, RPL (MAXSTP,MAXDEC,MINDEC,MINSTP), I don't unerdstand that...
        if (axis=="x") :
            self.send(self.xAxis, self.xCAN+"PVEL"+str(self.xID)+"=25000") # set max velocity
            self.send(self.xAxis, self.xCAN+"ACC"+str(self.xID)+"=100000") # set accerleration
            self.send(self.xAxis, self.xCAN+"RMK"+str(self.xID)+"="+refmask) # select reference point
            self.send(self.xAxis, self.xCAN+"RPL"+str(self.xID)+"="+refmask2) # ??
            self.send(self.xAxis, self.xCAN+"SMK"+str(self.xID)+"=1111") # switch mask for limits: all ON
            self.send(self.xAxis, self.xCAN+"SPL"+str(self.xID)+"=1111") # switch polarity: default
        else:
            self.send(self.yAxis, self.yCAN+"PVEL"+str(self.yID)+"=25000") # set max velocity
            self.send(self.yAxis, self.yCAN+"ACC"+str(self.yID)+"=100000") # set accerleration
            self.send(self.yAxis, self.yCAN+"RMK"+str(self.yID)+"="+refmask) # select reference point
            self.send(self.yAxis, self.yCAN+"RPL"+str(self.yID)+"="+refmask2) # ??
            self.send(self.yAxis, self.yCAN+"SMK"+str(self.yID)+"=1111") # switch mask for limits: all ON
            self.send(self.yAxis, self.yCAN+"SPL"+str(self.yID)+"=1111") # switch polarity: default

        
    def send(self, dev, command): # function for sending commands to the stage
        dev.write(command + "\r")
        time.sleep(0.05)
        return dev.read(1024).strip()
 
