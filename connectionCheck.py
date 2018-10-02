#!/usr/bin/python   

import serial       
import time
import sys

from VC840 import * # VC840 multimeter
from AxisHelper import *

def doConnectionCheck():
	ready = True
	print ""
	print ""
	print "Testing connections needed for calibration setup:"
	print ""
	print "Testing x/y axis connections:"
        isSPOCK=False
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
                        print send(axisControl1, "STOP1")
                        print send(axisControl1, "STOP2")
                        print send(axisControl1, "RESETMB")
                        print send(axisControl1, "ERRCLEAR")
                        print send(axisControl1, "EFREE1")
                        print send(axisControl1, "EFREE2")
                        print send(axisControl1, "01STOP1")
                        print send(axisControl1, "01STOP2")
                        print send(axisControl1, "01RESETMB")
                        print send(axisControl1, "01ERRCLEAR")
                        print send(axisControl1, "01EFREE1")
                        print send(axisControl1, "01EFREE2")
                        print send(axisControl1, "00STOP1")
                        print send(axisControl1, "00STOP2")
                        print send(axisControl1, "00RESETMB")
                        print send(axisControl1, "00ERRCLEAR")
                        print send(axisControl1, "00EFREE1")
                        print send(axisControl1, "00EFREE2")
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
	print "Checking communication with multimeter:"
	try:
                port="/dev/ttyUSB5"
		vc = VC840(port=port)
                print "    connecting to device at " + port 
		print "    serial port access OK"
		try:
		        vc._read_raw_value()
			print "    communication OK"
		except ValueError, e:
			print "    communication not OK -> FIX!!!"
			raise RuntimeError("Multimeter not working!")
	
	except:
		print "    multimeter not OK -> FIX!!!"
		ready = False

	print ""
	if ready: print "All checks are OK! You are ready to Go!!!"
	if not ready: print "Not all checks are OK! Please fix everything and redo this test!!!"

if __name__ == "__main__":
	doConnectionCheck()
	sys.exit
