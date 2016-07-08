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

print "measuring 1 minute: "

for i in range(6):
    try:
        vc._read_raw_value()
    except ValueError, e:
	print e
        continue

    if not vc.data:
        print 'no data'
        continue

    vc.decode()
    if vc.Error:
        print 'decoding error'
        continue

    print '%.2f' % time.time(),
    print vc.value, vc.unit,
    if vc.AC:
        print "AC"
    elif vc.DC:
        print "DC"
    else:
        print 'None'

    time.sleep(10)

