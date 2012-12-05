#!/usr/bin/env python

import struct
from bitarray import bitarray
from array import array
import pickle

"""
The data in a packet is in big-endian format. There are 5 8-bit bytes in 
a packet.
"""

# These bits should be set to 1 when the protocol is working
SYNC_BITS_SET = (0x80 << (8 * 4))

# These bits should be set to 0 when the protocol is working
SYNC_BITS_CLEAR = (0x80 << (8 * 3)) | (0x80 << (8 * 2)) | (0x80 << (8 * 1)) | 0x80

# Various indicator bits -- byte 0
CMS_BEEP    = 0x40 
CMS_SO2_LOW = 0x20
CMS_SEEK    = 0x10
# indicator bits -- byte 2
CMS_SEARCH  = 0x20
CMS_ERROR   = 0x10

# Various masks
# byte 0
CMS_STRENGTH = 0x0F
# byte 1
CMS_WAVEFORM = 0x7F
# byte 2
CMS_BARGRAPH = 0x0F
CMS_PULSERATE_A = 0x40
# byte 3
CMS_PULSERATE_B = 0x7F
# byte 4
CMS_O2_SAT   = 0x7F

class CmsPulseOx:
    """CmsPulseOx interprets data packets from some arbitrary input
    based on the protocol described in cms_protocol.pdf
    """

    def __init__(self):
        self.savefile = None
        self.loadfile = None

    def set_savefile(self, path):
        """ Open a file to save pulse ox data into. Data is saved
        using Python's native pickle format """
        self.savefile = open(path, 'a+b')

    def stop_saving(self):
        """ Close any open dump file """
        self.savefile.close()
        self.savefile = None

    def set_loadfile(self, path):
        """ Open a previously-saved datastream and process it as if
        it were being read in from the device live """
        self.loadfile = open(path, 'r')

    def read(self):
        while True:
            try:
                yield pickle.load(self.loadfile)
            except EOFError:
                return

    def sanity(self, data):
        """ Should be called for each packet of 5 bytes of data read
        in from the device. This method checks the sync bits of each
        byte in the packet, according to the schema:

        - byte 0 should have bit 7 HIGH
        - bytes 1-4 should have bit 7 LOW
        """
        # first byte has high bit set for sync
        if (not(data[0] & 0x80)):
            print "SYNC error in packet 0"
            return False
        # remaining bytes have high bit cleared for sync
        for i in xrange(1, 5):
            if (data[i] & 0x80):
                print "SYNC error in packet %d" % i
                return False
        return True

    def parse(self, packet):
        """ Parse out the bitfields from each data packet. There is some
        reconstruction necessary during this process, as at least one
        bitfield (pulse rate) is spread across two bytes, broken by a
        sync bit.

        Sets values on the instance object.
        """
        data = bytearray(packet)
        if self.sanity(data):
            if (data[0] & CMS_BEEP):
                self.beep = True
            else:
                self.beep = False

            if (data[0] & CMS_SO2_LOW):
                self.o2_low = True
            else:
                self.o2_low = False

            if (data[0] & CMS_SEEK):
                self.seek = True
            else:
                self.seek = False

            if (data[2] & CMS_SEARCH):
                self.search = True
            else:
                self.search = False

            if (data[2] & CMS_ERROR):
                self.error = True
            else:
                self.error = False

            self.strength = data[0] & CMS_STRENGTH
            self.waveform = data[1] & CMS_WAVEFORM
            self.bargraph = data[2] & CMS_BARGRAPH
            self.pulserate = data[2] & CMS_PULSERATE_A
            self.pulserate |= data[3] & CMS_PULSERATE_B
            self.o2_sat = data[4] & CMS_O2_SAT

            if self.savefile:
                # we should prepend each packet with a timestamp
                # so that we can create meaningful data streams
                # for later parsing
                pickle.dump(packet, self.savefile, pickle.HIGHEST_PROTOCOL)

            return True
        else:
            return False

    def dump(self):
        """ Output a printable string based on the most recently read-in
        packet """
        return "{0:5s} | {1:6s} | {2:5s} | {3} | {4:08b} | {5:5s} | {6:3s} | {7:02d} | {8:3d} bpm | {9:2d}% |".format(
            "beep" if self.beep else "",
            "O2 low" if self.o2_low else "",
            "seek" if self.seek else "",
            self.strength,
            self.waveform,
            "srch" if self.search else "",
            "ERR" if self.error else "",
            self.bargraph,
            self.pulserate,
            self.o2_sat
        )
