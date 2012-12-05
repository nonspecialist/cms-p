#!/usr/bin/env python
#
# Simply dump out the CMS-P protocol from the serial port
#

from cmspulseox import CmsPulseOx

pulseox = CmsPulseOx()

pulseox.set_loadfile("dump.pickle")

for packet in pulseox.read():
    if pulseox.parse(packet):
        print pulseox.dump()
