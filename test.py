#!/usr/bin/env python


from subprocess import Popen, PIPE, STDOUT
import sys
import re
import time
import os
import binascii
from bitstring import BitArray
from crccheck.crc import CrcBase
import models.firmware_package_pb2 as firmware
import serial
import zlib


class CrcSTM(CrcBase):
    """CRC-STM"""
    _width = 32
    _poly = 0x4C11DB7
    _initvalue = 0xFFFFFFFF
    _reflect_input = False
    _reflect_output = False
    _xor_output = 0x0
    _check_result = 0x376e6e7


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
        crc = CrcSTM()
        checksum_data = 0
        proceed = 0
        first_message = 1
        while True:
            p = term.readline()
            while True:
                if p != b'' and p!=b'\xff\n' and p!=b'\xff':
                    try:
                        p = p[:-1]
                        status_msg = firmware.status()

                        status_msg.ParseFromString(p)
                        if status_msg.status == firmware.status.status_enum.READY:
                            if first_message:
                                first_message = 0
                                proceed = 1
                            else:
                                proceed = 0
                            print('.', end='')
                            sys.stdout.flush()
                            break
                        if status_msg.status == firmware.status.status_enum.ACK:
                            proceed = 1
                            print('.', end='')
                            sys.stdout.flush()
                            break
                        if status_msg.status == firmware.status.status_enum.REJECT:
                            proceed = 0
                            break

                    except:
                        print("\n[DEBUG MESSAGE]")
                        print(p)
                p = term.readline()

            if proceed == 1:
                if (last_line):
                    break
                packet = firmware.firmware_packet()
                packet.line.record_type = f.read(2)
                if(packet.line.record_type == "S5"):
                    last_line = 1
                packet.line.byte_count = int(f.read(2), 16)
                packet.line.address = int(f.read(4), 16)
                packet.line.data = (binascii.a2b_hex(
                    f.read(2*packet.line.byte_count-6)))
                packet.line.checksum = int(f.read(2), 16)
                checksum_data = b'\x00\x00' + \
                    bytes(packet.line.record_type, 'utf-8')
                checksum_data = checksum_data + \
                    packet.line.byte_count.to_bytes(4, byteorder='big')
                checksum_data = checksum_data + \
                    packet.line.address.to_bytes(4, byteorder='big')
                checksum_data = checksum_data + \
                    packet.line.checksum.to_bytes(4, byteorder='big')
                if(not last_line == 1):
                    checksum_data = checksum_data + packet.line.data
                    while len(checksum_data) % 4:
                        checksum_data = checksum_data + b'\x00'

                packet.checksum = crc.calc(checksum_data)
                f.read(1)
            else:
                print("\n[DEBUG MESSAGE]")
                print(packet.SerializeToString())
            

            term.write(bytes([packet.ByteSize()]))
            term.write(packet.SerializeToString())

        print("\nFinished sending firmware!")
        while True:
            p = term.readline()
            if p != b'':
                print(p)
                sys.stdout.flush()
