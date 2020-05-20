#!/usr/bin/env python


from subprocess import Popen, PIPE, STDOUT
import sys
import re
import time
import os
import binascii
from bitstring import BitArray
import crcmod
from models.firmware_package_pb2 import *
import serial

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

FIRMWARE_LOCATION = "./firmware/firmware.srec"

if(len(sys.argv) < 2):
    print("USING DEFAULT LOCATION \"", FIRMWARE_LOCATION, "\"")

fileSize = os.path.getsize(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION))
print("Firmware size: ", fileSize)

with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as term:
    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION), "r") as f:
        print("Executing firmware upgrade")
        last_line = 0
        while True:

            p = term.readline()
            while p != b'hi\n':
                if p != b'':
                    print(p)
                p = term.readline()

            line = srec_line()
            line.record_type = f.read(2)
            if(line.record_type == "S5"):
                last_line = 1
            line.byte_count = int(f.read(2), 16)
            line.address = int(f.read(4), 16)
            bla = f.read(2*line.byte_count-6)
            line.data=(binascii.a2b_hex(bla))
            line.checksum = int(f.read(2), 16)
            term.write(bytes([line.ByteSize()]))
            term.write(line.SerializeToString())
            if (last_line):
                break
            f.read(1)

        print("Finished sending firmware!")
        while True:
            p = term.readline()
            if p != b'':
                print(p)
                sys.stdout.flush()
