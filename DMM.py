# -*- coding: utf-8 -*-

import serial
import time

class DMM(object):

    def __init__(self, port="/dev/ttyUSB1"):
        """ """
        print ("DMM, init with port : " + port)
        self.port = port
        self.serial = serial.Serial('/dev/ttyUSB0', baudrate=19200, timeout=0.)


    def send_receive(self,command):
        print("DMM command: " + command)
        self.serial.write(command + '\n')
        received = ""
        char = self.serial.read()
        while char != '\n':
            if char == '\n':
                break
            received += char
            char = self.serial.read()

        #received = ser.read(100)
        #received = received.replace('\n','')
        print ("received: " + received)
        return received


    def readVoltage(self, prefix):
        V = float(self.send_receive('READ?'))
        if (prefix == 'm'):
            V *= 1000
        return V

    
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

    


    
    
