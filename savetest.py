#!/usr/bin/env python
#
# Simply dump out the CMS-P protocol from the serial port
#

import serial
from cmspulseox import CmsPulseOx

RETRIES_MAX = 10

pulseox = CmsPulseOx()
pulseox.set_savefile("dump.pkl")
pulseox.set_serial()

count = 0
retries = RETRIES_MAX

for tstamp, packet in pulseox.read():
    if pulseox.parse(packet):
        print "{0:10.02f}:{1}".format(tstamp, pulseox.dump())
    else:
        print "bad packet"
    count += 1

    if (count > 10000):
        break

pulseox.stop_saving()
