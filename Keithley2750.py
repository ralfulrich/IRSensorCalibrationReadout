# -*- coding: utf-8 -*-

import serial
import time

class Keithley2750(object):

    def __init__(self, port="/dev/ttyUSB?",verbose=False,isDummy=False):
        """ """
        self.isDummy = isDummy
        if (self.isDummy):
            return
        self.verbose = verbose
        print ("Keithley2750, init with port : " + port)
        if (self.verbose):
            print ("->make sure that your 27xx is configured for RS232 control!")
        iPort = 0
        while True:
            self.port = port
            if ("?" in port):
                self.port = port.replace("?", str(iPort))
            try:

                print (self.port)
                self.serial = serial.Serial(self.port, baudrate=19200, xonxoff=True, timeout=1)
                # time.sleep(.5)
                self.IDN = self.send_receive("*IDN?")
                self.send("*OPC")
                print("IDN=\'" + self.IDN + "\'")
                if ("2750" not in self.IDN):
                    iPort += 1
                    continue
                
                self.send("SYST:PRES")
                self.send("*RST")
                self.send("*CLS")
                #self.send("INIT:CONT")
                self.send("ABOR")
                self.send("*OPC")
                self.send("INIT:CONT OFF")
                self.send("TRIG:COUN 1")
                self.send("SAMP:COUN 1")
                self.send("*OPC")
                self.previousChan = "unknown"
                print ("Keithley, init with port : " + self.port)
                break
            except:
                iPort += 1
                if (("?" not in port) or iPort == 20):
                    raise

                
        
    def waitMilli(self, ms) :
        time.sleep(ms/1000.)
        #millis0 = int(round(time.time() * 1000))
        #while (True) :
        #    millis1 = int(round(time.time() * 1000))
        #    if (millis1-millis0 > ms) :
        #        break

            
    def getPort(self):
        return self.port
        
        
    def send(self, command):
        if (self.isDummy):
            return
        #time.sleep(0.1)
        if (self.verbose):
            print("Keithley2750 write command: " + command)

        nTry = 0
        while True:
            try:
                self.serial.write(command + '\r')
                self.waitMilli(50)
                break
            except serial.SerialException as e:
                nTry += 1
            if nTry > 5:
                print("Serious error in Keitley::send \'" + command + "\'")
                break
                
        

    def send_receive(self,command):
        if (self.isDummy):
            return 0.0
        self.send(command)
        received = ""
        char = ""
        while char != '\r':
            try:
                self.waitMilli(10)
                char = self.serial.read()
            except serial.SerialException as e:
                print ("Serious error in Keithley::read. Return 0.")
                return "0.0"
            if char:
                received += char
            else:
                break
        if (self.verbose):
            print ("received: " + received)
        return received

    
    def send_receive_new(self,command):
        if (self.isDummy):
            return 0.0
        self.send(command)
        self.waitMilli(50)
        received = ""
        while True:
            try:
                received = self.serial.read(1024)
            except serial.SerialException as e:
                print ("SerialException Keithley::send cmd=" + command  + " " + str(e))
                continue
            break            
        if (self.verbose):
            print ("received: " + received)
        return received.strip() 


    def connectChannel(self, chan):
        if (chan==self.previousChan):
            return
        self.previousChan = chan
        self.send("ROUT:CLOS (" + chan + ")")
        self.send("*WAI")
        self.send("*OPC")

        
    def readVoltage(self, prefix):
        self.send("*WAI")
        V = self.convert(self.send_receive('READ?'))
        if (prefix == 'm'):
            V *= 1000
        return V
    
    
    # +1.12006772E+00VDC,+0.000SECS,+00000RDNG#
    def convert(self, data):
        if (self.isDummy):
            return 0.0
        try:
            return float(data.split(',')[0].replace("VDC",""))
        except ValueError:
            return 0.0
    
    
    def readStable(self, nMeas=1, accuracy=0.025):
        if (self.isDummy):
            return [0.0]
        # check for stability
        nRead = 0
        previous = None
        data = None
        for m in range(20):
            nRead += 1
            self.waitMilli(50)
            data = self.readVoltage("m")
            if (data!=None and previous!=None):
                if (data!=0) :
                    #if (data==0 and previous==0) or (abs(data-previous)/data < accuracy):
                    if (abs(data-previous) < abs(data*accuracy)):
                        break
            previous = data

        # save nMeas-2 values
        voltage = [previous, data]
        for m in range(nMeas-2):
            while True:
                meas = self.readVoltage("m")
                if meas:
                    voltage.append(meas)
                    break

        if (self.verbose):
            print ("keithley, read_stable, nRead=%d" % nRead)
                
        return voltage

    


    
    
