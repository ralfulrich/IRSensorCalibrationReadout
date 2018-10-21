import sys
import serial
import time

from VC840 import *

print "trying to initialize VC480"
try:
    vc = VC840()
except serial.serialutil.SerialException, err:
    print err
    sys.exit()
print "    done"

nMeas = 100
print "I will measure", nMeas, "values"

for i in range(nMeas):
    voltage = vc.readVoltage("m")
    if voltage:
	print voltage
