#!/usr/bin/python   

import serial       
import time
import sys

from DMM import *

dmm = DMM(port="/dev/ttyUSB10")

print (str(dmm.readVoltage("m")))

print (str(dmm.readTemperature()))

print (str(dmm.readStable(5)))
