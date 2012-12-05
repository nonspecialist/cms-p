#!/usr/bin/env python
#
# Simply dump out the CMS-P protocol from the serial port
#

import serial
import time
from cmspulseox import CmsPulseOx

RETRIES_MAX = 10

def openserial():
    return serial.Serial('/dev/ttyUSB0', 19200)

ser = openserial()
pulseox = CmsPulseOx()

count = 0
retries = RETRIES_MAX

while count < 10000:
    # Wait until we have enough to read a packet
    if (ser.inWaiting() < 5):
        continue

    packet = ser.read(5)
    if pulseox.parse(packet):
        print pulseox.dump()
    else:
        print "bad SYNC, re-trying"
        trash = ser.read(1)
        retries -= 1

    count += 1

if not retries:
    print "Could not achieve sync after %d tries" % RETRIES_MAX
