#!/usr/bin/python   

import serial       
import time
import sys

from VC840 import * # VC840 multimeter
from AxisHelper import *
from DMM import *
from Keithley2750 import *

import smtplib
from email.mime.text import MIMEText

# def getK(mult):
#         received = ""
#         #received = mult.readline()
#         #print (received)
#         #return received
        
#         char = mult.read()
#         while char != '\r':
#             if char == '\r':
#                 break
#             received += char
#             char = mult.read()
#         print (received)
#         return received
def send(dev, command): # function for sending commands to the stage
        dev.write(command + "\r")
        time.sleep(0.05)
        return dev.read(1024).strip()


def doConnectionCheck():
	ready = True

        #data="+1.12006772E+00VDC,+0.000SECS,+00000RDNG#"
        #print str(float(data.split(',')[0].replace("VDC","")))
        #data="-1.19874016E-06VDC,+0.312SECS,+00003RDNG#"
        #print str(float(data.split(',')[0].replace("VDC","")))
        
        print ""
	print ""
	print "Testing connections needed for calibration setup:"
	print ""
	print "Testing x/y axis connections:"
        isSPOCK = False
	try:
		axisControl1 = serial.Serial("/dev/ttyACM0")
		axisControl1.baudrate = 9600
		axisControl1.timeout = 0.2
		print "    Axis 1 connection OK"
		try:
			print "    Axis 1 communications protocol" , send(axisControl1, "TERM=2") # response with plain text and 'OK'
		except:
			print "    Axis 1 communications protocol not OK -> FIX!!!"
			raise RuntimeError("Axis not working!")
		try:
			serNum1 = send(axisControl1, "?SERNUM")
			print "    Axis 1 serialnumber", serNum1
			if (serNum1 == "14080004"):  # short one
                                print "        this is the x-Axis"
			elif (serNum1 == "14080003"):  #short one  
				print "        this is the y-Axis"
                        elif (serNum1 == "12070211"): # SPOCK
                                print " this is SPOCK"
                                isSPOCK=True
			else:
				print "        I don't know this serial number -> FIX!!!"
			print "    Axis 1 status \'" + send(axisControl1, "?ASTAT") + "\'"
                        
                        send(axisControl1, "00INIT1")
                        send(axisControl1, "00EFREE1")
                        
                        send(axisControl1, "01INIT1")
                        send(axisControl1, "01EFREE1")
                        
                        send(axisControl1, "00STOP1")
                        send(axisControl1, "01STOP1")
                        
                        print(send(axisControl1, "00?MSG"))
                        print(send(axisControl1, "01?MSG"))

                        #send(axisControl1, "RESETMB")
                        #send(axisControl1, "00RESETMB")
                        #send(axisControl1, "01RESETMB")
                        #send(axisControl1, "ERRCLEAR")
                        #send(axisControl1, "00ERRCLEAR")
                        #send(axisControl1, "01ERRCLEAR")


                except:
			print "Axis 1 communication not OK -> FIX!!!"
			raise RuntimeError("Axis not working!")
		print "    Axis 1 OK and working !"
		print ""
	except:	
		print "    Axis 1 not OK -> FIX!!!"
		print ""
		ready = False

        if (not isSPOCK):
	        try:
                        axisControl2 = serial.Serial("/dev/ttyACM1")
                        axisControl2.baudrate = 9600
                        axisControl2.timeout = 0.2
                        print "    Axis 2 connection OK"
                        try:
                                print "    Axis 2 communications protocol" , send(axisControl2, "TERM=2") # response with plain text and 'OK'
                        except:
                                print "    Axis 2 communications protocol not OK -> FIX!!!"
                                raise RuntimeError("Axis not working!")
                        try:
                                serNum2 = send(axisControl2, "?SERNUM")
                                print "    Axis 2 serialnumber", serNum1
                                if serNum2 == "14080004":
                                        print "        this is the x-Axis"
                                elif serNum2 == "14080003":
                                        print "        this is the y-Axis"
                                else:
                                        print "        I don't know this serial number -> FIX!!!"
                                print "    Axis 2 status", send(axisControl2, "?ASTAT")
                        except:
                                print "Axis 2 communication not OK -> FIX!!!"
                                raise RuntimeError("Axis not working!")
                        print "    Axis 2 OK and working !"
                        print ""
                except:
                        print "    Axis 2 not OK -> FIX!!!"
                        print ""
                        ready = False
 

        print ""
	print ""	
	print "Checking communication with multimeter U1272A:"

        dmm = DMM(port="/dev/ttyUSB5")
        print (str(dmm.readVoltage("m")))
        print (str(dmm.readTemperature()))
        print (str(dmm.readStable(nMeas=5, accuracy=0.025)))

        
        print ""
	print ""	
	print "Checking communication with multimeter V840:"
        #                port="/dev/ttyUSB?" # scan for right device
        #port="/dev/ttyUSB0"  
        port="/dev/ttyUSB6"  
        #port="/dev/ttyUSB5" # ...  
	vc = VC840(port=port)
        print "    connecting to device at " + vc.getPort()
	print "    serial port access OK"
	try:
                vc._read_raw_value()
		print ("read = " + str(vc.readCurrent("m")))
		print "    communication OK"
	except ValueError, e:
		print "    communication not OK -> FIX!!!"
		raise RuntimeError("Multimeter not working!")
	


                
        if (isSPOCK):
                print ("\n\n\n\n")
                print ("try Keitley")
                port="/dev/ttyUSB7" # use ? to scan for right device
                #port="/dev/ttyUSB6" # use ? to scan for right device
                #port="/dev/ttyUSB1" # use ? to scan for right device
		k2750 = Keithley2750(port=port, verbose=True)
                print "    connecting to device at " + k2750.getPort()
		print "    serial port access OK"
                
                k2750.connectChannel("@101")
                k2750.readVoltage("m")
                v=k2750.readStable(2)
                print ("result: " + str(v))
                
                k2750.connectChannel("@102")
                k2750.readVoltage("m")
                v=k2750.readStable(2)
                print ("result: " + str(v))
                
                k2750.connectChannel("@103")
                k2750.readVoltage("m")
                k2750.readStable(2)
                print ("result: " + str(v))
                
                k2750.connectChannel("@104")
                k2750.readVoltage("m")
                v=k2750.readStable(2)
                print ("result: " + str(v))
                
                doStress = True
                if doStress:
                        for i in range(50):
                                for j in range(4):
                                        ch = i%4
                                        k2750.connectChannel("@10"+str(ch+1))
                                        v = k2750.readStable(5)
                                        print (str(i) + "   " + str(v))
                                
                        

        print ("send email")
        email = "works!\n"
        msg = MIMEText(email)
        msg['Subject'] = 'IR sensor scan test'
        msg['From'] = "spock@kit.edu"
        msg['To'] = "ralf.ulrich@kit.edu"
        s = smtplib.SMTP('smtp.kit.edu',25)
        s.sendmail("CASTORgroup@kit.edu", ["ralf.ulrich@kit.edu"], msg.as_string())
        s.quit()

                        
	print ""
	if ready: print "All checks are OK! You are ready to Go!!!"
	if not ready: print "Not all checks are OK! Please fix everything and redo this test!!!"
        print ""





        # mult = serial.Serial("/dev/ttyUSB1", baudrate=9600, xonxoff=True, timeout=5)

        # print(mult.write("*RST\r"))
        # print(mult.write("*CLS\r"))
        # #print(mult.write("INIT:CONT\r"))
        # print(mult.write("SYST:PRES\r"))
        # print(mult.write("ABOR\r"))
        # print(mult.write("*RST\r"))
        # print(mult.write("*OPC\r"))
        # print(mult.write("*IDN?\r"))
        # getK(mult)
        
        # print(mult.write("INIT:CONT OFF\r"))
        # print(mult.write("TRIG:COUN 1\r"))
        # print(mult.write("SAMP:COUN 5\r"))
        
        # #print(mult.write("SENS:FUNC VOLT:AC\r"))
        # print(mult.write("ROUT:OPEN:ALL" + '\r'))
        # print(mult.write("ROUT:CLOS (@403)" + '\r'))
        # #print(mult.write('ROUT:CLOS (@103)\r'))
        # #print(mult.write("READ?" + '\r'))
        # #print(mult.write("INIT\r"))
        # print(mult.write("*OPC\r"))
        # print(mult.write("READ?\r"))
        # #print (mult.write("MEAS:VOLT:DC? 10, 0.01, (@101)\r"))        
        # getK(mult)

        # time.sleep(1)
        
        # print(mult.write("ROUT:CLOS (@402)" + '\r'))
        # print(mult.write("READ?\r"))
        # getK(mult)
        
        # time.sleep(1)

        # print(mult.write("ROUT:CLOS (@403)" + '\r'))
        # print(mult.write("READ?\r"))
        # getK(mult)

        return ready


        
if __name__ == "__main__":
	doConnectionCheck()
	sys.exit
