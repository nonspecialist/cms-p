#!/usr/bin/env python
#
# Simply dump out the CMS-P protocol from the serial port
#

import serial
from cmspulseox import CmsPulseOx

RETRIES_MAX = 10

def openserial():
    return serial.Serial('/dev/ttyUSB0', 19200)

ser = openserial()
pulseox = CmsPulseOx()

pulseox.set_savefile("dump.pkl")

count = 0
retries = RETRIES_MAX

while count < 1000:
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

pulseox.stop_saving()

if not retries:
    print "Could not achieve sync after %d tries" % RETRIES_MAX
