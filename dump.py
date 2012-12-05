#!/usr/bin/env python
#
# Simply dump out the CMS-P protocol from the serial port
#

import serial

ser = serial.Serial('/dev/ttyUSB0', 19200)

while True:
    packet = bytearray(ser.read(5))

    # sanity checks
    if (not(packet[0] & 0x80)):
        print "packet 0 SYNC bit missing"
        continue

    if (packet[1] & 0x80):
        print "packet 1 SYNC bit wrong"
        continue

    if (packet[2] & 0x80):
        print "packet 2 SYNC bit wrong"
        continue

    if (packet[3] & 0x80):
        print "packet 3 SYNC bit wrong"
        continue

    if (packet[4] & 0x80):
        print "packet 4 SYNC bit wrong"
        continue

    # Set the output display
    # First packet
    if (packet[0] & 0x40):
        out = "beep | "
    else:
        out = "     | "

    if (packet[0] & 0x20):
        out += "SO2 V | "
    else:
        out += "      | "

    if (packet[0] & 0x10):
        out += "seek | "
    else:
        out += "     | "

    strength = (packet[0] & 0x0F)
    out += str(strength)

    # Second packet - waveform
    out += " | {0:07b} | ".format(packet[1] & 0x7F)

    # Third  & fourth packets
    if (packet[2] & 0x20):
        out += "searching | "
    else:
        out += "          | "

    if (packet[2] & 0x10):
        out += "ERR | "
    else:
        out += "    | "

    bar = packet[2] & 0x0F

    out += "{0:02d} | ".format(bar)

    # Bit 7 of the pulse rate comes from bit 6 of third byte, plus bits
    # 0-6 of fourth byte
    rate = packet[2] & 0x40
    rate |= (packet[3] & 0x7F)

    out += "{0:3d}".format(rate) + " bpm | "

    # Fifth packet
    # bytes 0-6 give us the O2 sat
    o2sat = (packet[4] & 0x7F)
    out += "{0:3d}".format(o2sat) + " |"

    print out

ser.close()
