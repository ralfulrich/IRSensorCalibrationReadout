# -*- coding: utf-8 -*-

import sys
import serial
import time

class seven_element_digit(object):
    """ """
    def __init__(self, b1, b2):
        """ """
        self.elements = self.decode(b1, b2)
        self.value = self.digit()

    def digit(self):
        """ get numerical digit from the list of active segments """
        digit = self.elements
        if digit == [1, 1, 1, 1, 1, 1, 0]:
            return 0
        elif digit == [0, 1, 1, 0, 0, 0, 0]:
            return 1
        elif digit == [1, 1, 0, 1, 1, 0, 1]:
            return 2
        elif digit == [1, 1, 1, 1, 0, 0, 1]:
            return 3
        elif digit == [0, 1, 1, 0, 0, 1, 1]:
            return 4
        elif digit == [1, 0, 1, 1, 0, 1, 1]:
            return 5
        elif digit == [1, 0, 1, 1, 1, 1, 1]:
            return 6
        elif digit == [1, 1, 1, 0, 0, 0, 0]:
            return 7
        elif digit == [1, 1, 1, 1, 1, 1, 1]:
            return 8
        elif digit == [1, 1, 1, 1, 0, 1, 1]:
            return 9
        elif digit == [0, 0, 0, 1, 1, 1, 0]:  # 'L'
            return None
        elif digit == [0, 0, 0, 0, 0, 0, 0]:  # ' '
            return 0
        else:
            #print 'could not decode digit', digit
            raise ValueError('could not decode digit')

    def decode(self, b1, b2):
        """ decode which segments a..g are ON """
        this_digit = [0] * 7
        this_digit[0] = b1 & 0x1 > 0
        this_digit[5] = b1 & 0x2 > 0
        this_digit[4] = b1 & 0x4 > 0
        this_digit[1] = b2 & 0x1 > 0
        this_digit[6] = b2 & 0x2 > 0
        this_digit[2] = b2 & 0x4 > 0
        this_digit[3] = b2 & 0x8 > 0

        return this_digit



    
class VC840(object):

    UNIT = {'voltage': 'V',
            'current': 'A',
            'resistance': 'Ohm',
            'frequency': 'Hz',
            'temperature': 'u°C',
            'error': '?'}

    def __init__(self, port="/dev/ttyUSB0", isDummy=False):
        """ """
        self.isDummy = isDummy
        if (self.isDummy):
            return
        print ("VC840, init with port : " + port)
        if ("?" in port):
            iPort = 0
            while True:
                self.port = port.replace("?", str(iPort))
                try:
                    self.serial = serial.Serial(self.port,
                                                baudrate=2400,
                                                bytesize=8,
                                                parity="N",
                                                stopbits=1,
                                                timeout=1.5,
                                                xonxoff=0,
                                                rtscts=0,
                                                dsrdtr=None)
                    break
                except:
                    iPort += 1
                    
                if (iPort==9):
                    print ("-> This VC840 is NOT WORKING")
                    raise RuntimeError("This VC840 is NOT WORKING")

                    
        else:
            self.port = port
            self.serial = serial.Serial(self.port,
                                        baudrate=2400,
                                        bytesize=8,
                                        parity="N",
                                        stopbits=1,
                                        timeout=1.5,
                                        xonxoff=0,
                                        rtscts=0,
                                        dsrdtr=None)
        
        self.serial.setRTS(0)
        self.serial.setDTR(0)
        self.digit = [[0] * 7] * 4
        self.mode = None
        self.mrange = None
        self.data = None
        self.rs232 = None
        self.auto = None
        self.DC = None
        self.AC = None


    def getPort(self):
        return self.port

    
    def _read_raw_value(self):
        """ returns read bytes as list of integers """
        if (self.isDummy):
            return       
        for n in range(5):  # 5 attempts to read
            self.serial.flushInput()
            self.serial.setDTR(1)
            try:
                raw_data = self.serial.read(14)  # read 14 bytes
            except serial.serialutil.SerialException, err:
                print 'device disconnected'
                sys.exit()

            if not raw_data:
                self.serial.setDTR(0)
                self.serial.flushInput()
                raise ValueError("Communication timeout")

            self.serial.setDTR(0)
            self.serial.flushInput()

            d_bytes = list()
            for byte in raw_data:
                d_bytes.append(ord(byte))

            if len(d_bytes) == 14:  # we have all 14 bytes
                if not d_bytes == sorted(d_bytes):
                    d_bytes.sort()
                self.data = d_bytes
                return

        raise ValueError("could not read data from port")

    def decode(self):
        """ decode data telegram """
        if (self.isDummy):
            return
        # step 1: decode word for word
        word = self.data[0]
        self.rs232 = word & 0x1 > 0
        self.auto = word & 0x2 > 0
        self.DC = word & 0x4 > 0
        self.AC = word & 0x8 > 0

        self.Error = False
        try:
            self.negative = self.data[1] & 0x8 > 0
            self.digit4 = seven_element_digit(self.data[1], self.data[2])

            p1 = self.data[3] & 0x8 > 0
            self.digit3 = seven_element_digit(self.data[3], self.data[4])

            p2 = self.data[5] & 0x8 > 0
            self.digit2 = seven_element_digit(self.data[5], self.data[6])

            p3 = self.data[7] & 0x8 > 0
            self.digit1 = seven_element_digit(self.data[7], self.data[8])
        except ValueError, e:
            self.Error = True
            return

        word = self.data[9]
        self.diode_test = word & 0x1 > 0
        kilo = word & 0x2 > 0
        nano = word & 0x4 > 0
        mikro = word & 0x8 > 0

        word = self.data[10]
        self.beep = word & 0x1 > 0
        mega = word & 0x2 > 0
        self.duty_cycle = word & 0x4 > 0
        milli = word & 0x8 > 0

        word = self.data[11]
        self.hold = word & 0x1 > 0
        self.relative = word & 0x2 > 0
        ohm = word & 0x4 > 0
        capacity = word & 0x8 > 0

        word = self.data[12]
        self.low_battery = word & 0x1 > 0
        frequency = word & 0x2 > 0
        voltage = word & 0x4 > 0
        current = word & 0x8 > 0

        temperature = self.data[13] & 0x1 > 0

        # step 2: now group logically
        if mega:
            self.mrange = 1E6
        elif kilo:
            self.mrange = 1E3
        elif milli:
            self.mrange = 1E-3
        elif mikro:
            self.mrange = 1E-6
        elif nano:
            self.mrange = 1E-9
        else:
            self.mrange = 1.

        if p1:
            self.scale = 1.E-3
        elif p2:
            self.scale = 1.E-2
        elif p3:
            self.scale = 1.E-1
        else:
            self.scale = 1.

        if voltage:
            self.mode = 'voltage'
        elif ohm:
            self.mode = 'resistance'
        elif frequency:
            self.mode = 'frequency'
        elif current:
            self.mode = 'current'
        elif capacity:
            self.mode = 'capacity'
        elif temperature:
            self.mode = 'temperature'
        else:
            self.mode = 'error'

        self.unit = self.UNIT[self.mode]

        if self.negative:
            self.sign = -1
        else:
            self.sign = 1
        try:
            self.value = (1e3 * self.digit4.value
                          + 1e2 * self.digit3.value
                          + 1e1 * self.digit2.value
                          + self.digit1.value)
            self.value *= self.scale * self.mrange * self.sign
        except TypeError:
            # should happen only for Ohm measurements when 'L' is displayed
            self.value = 'Inf'


            
    def readVoltage(self,prefix):
        if (self.isDummy):
            return None
       
        try:
            self._read_raw_value()
        except ValueError, e:
            return None

        if not self.data:
            return None

        self.decode()
        if self.Error:
            return None

        if self.unit != "V":
            return None

	if self.value == 'Inf':
	    return None

	if prefix == "m":
	    return self.value*1000.
	else:
	    return self.value

        #time.sleep(0.001)


        
    def readCurrent(self,prefix):
        if (self.isDummy):
            return None

        try:
            self._read_raw_value()
        except ValueError, e:
            return None

        if not self.data:
            return None

        self.decode()
        if self.Error:
            return None

        if self.unit != "A":
            return None

	if self.value == 'Inf':
	    return None

	if prefix == "m":
	    return self.value*1000.
	else:
	    return self.value


        
    def readStable(self, nMeas):

        voltage = []
        if (self.isDummy):
            return [0.0]

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

    
