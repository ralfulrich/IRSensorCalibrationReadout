# -*- coding: utf-8 -*-

import serial
import time

class Keithley2750(object):

    def __init__(self, port="/dev/ttyUSB1"):
        """ """
        print ("Keithley2750, init with port : " + port)
        print ("->make sure that your 27xx is configured for RS232 control!")
        self.port = port
        self.serial = serial.Serial(self.port, baudrate=9600, xonxoff=True, timeout=1)

        self.send("*RST")
        self.send("*CLS")
        #self.send("INIT:CONT")
        self.send("SYST:PRES")
        self.send("ABOR")
        self.send("*RST")
        self.send("*OPC")
        self.send("INIT:CONT OFF")
        self.send("TRIG:COUN 1")
        self.send("SAMP:COUN 1")
        self.IDN = self.send_receive("*IDN?")
        print("IDN=" + self.IDN)

        
    def getPort(self):
        return self.port
        
        
    def send(self, command):
        print("Keithley2750 write command: " + command)
        self.serial.write(command + '\r')
        

    def send_receive(self,command):
        self.send(command)
        received = ""
        char = self.serial.read()
        while char != '\r':
            if char == '\r':
                break
            received += char
            char = self.serial.read()
        print ("received: " + received)
        return received


    def connectChannel(self, chan):
        self.send("ROUT:CLOS (" + chan + ")")

        
    def readVoltage(self, prefix):
        V = self.convert(self.send_receive('READ?'))
        if (prefix == 'm'):
            V *= 1000
        return V
    
    
    # +1.12006772E+00VDC,+0.000SECS,+00000RDNG#
    def convert(self, data):
        return float(data.split(',')[0].replace("VDC",""))
    
    
    def readStable(self, nMeas):
        voltage = []        
        # check for stability
        for m in range(20):
            tmp1 = None
            tmp2 = None
            while tmp1 == None or tmp2==None:
                tmp1 = self.readVoltage("m")
                time.sleep(0.2)
                tmp2 = self.readVoltage("m")
            if (tmp1-tmp2)<(0.025*tmp1):
                break

        # save nMeas values
        for m in range(nMeas):
            while True:
                meas = self.readVoltage("m")
                if meas:
                    voltage.append(meas)
                    break

        return voltage

    


    
    
