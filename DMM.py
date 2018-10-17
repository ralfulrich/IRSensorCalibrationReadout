# -*- coding: utf-8 -*-

import serial
import time

class DMM(object):

    def __init__(self, port="/dev/ttyUSB10"):
        """ """
        print ("DMM, init with port : " + port)
        iPort = 0
        while True:
            self.port = port
            if ("?" in port):
                self.port = port.replace("?", str(iPort))
            try:
                self.serial = serial.Serial(self.port, baudrate=19200, timeout=.1)
                time.sleep(1)
                self.send_receive("RST")
                print('meter,  identifying meter: ' + self.send_receive("?IDN?"))
                print('meter,  Battery: ' + self.send_receive("SYST:BATT?"))
                print('meter,  Config: ' + self.send_receive("CONF?"))
                print ("DMM, init with port : " + self.port)
                break
            except:
                iPort += 1
                if (("?" not in port) or iPort == 20):
                    raise

            
    def send_receive(self,command, length=200):
        self.send(command)
        time.sleep(0.25)
        received = ""
        while True:
            try:
                received = self.serial.read(1024)
            except serial.SerialException as e:
                print ("SerialException DMM::send cmd=" + command  + " " + str(e))
                continue
            break            
        return received.strip() 

    
    def send(self, cmd):
        self.serial.write(cmd + "\n")
        time.sleep(0.25)

    
    def readVoltage(self, prefix=""):
        V = self.read_meter("no")
        if (prefix == 'm'):
            V *= 1000
        return V

    
    def readTemperature(self):
        V = self.read_meter("yes")
        return V

    
    def read_meter(self, second='no'):

        responsestr = ""
        if second != 'yes' :
            responsestr = self.send_receive("FETC?", length=17)
        else :
            responsestr = self.send_receive("FETC? @2", length=17)
        response = float(responsestr)
        return response



    
    def readStable(self, nMeas=2, accuracy=0.025):

        nRead = 0
        previous = None
        data = None
        for m in range(20):
            nRead += 1
            data = self.readVoltage("m")
            if (data!=None and previous!=None):
                if (data!=0) :
                    #if (data==0 and previous==0) or (abs(data-previous)/data < accuracy):
                    if (abs(data-previous) < abs(accuracy*data)):
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

        return voltage

    


    
    
