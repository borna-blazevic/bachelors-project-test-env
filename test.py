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
import random


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

FIRMWARE_LOCATION1 = "./firmware/firmware1.srec"
FIRMWARE_LOCATION2 = "./firmware/firmware2.srec"
FIRMWARE_LOCATION3 = "./firmware/firmware3.srec"
FIRMWARE_LOCATION4 = "./firmware/firmware4.srec"

if(len(sys.argv) < 2):
    print("USING DEFAULT LOCATION \"", FIRMWARE_LOCATION1, "\"")

fileSize = os.path.getsize(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION1))
print("Firmware size: ", fileSize)

with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as term:
    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION1), "r") as f:
        print(bcolors.OKBLUE + bcolors.BOLD +
              "EXECUTING TEST 1" + bcolors.ENDC)
        last_line = 0
        crc = CrcSTM()
        checksum_data = 0
        proceed = 0
        first_message = 1
        test_success = 0
        packet = None
        while True:
            while True:
                p = term.readline()
                p = p.replace(b'\xff', b'')
                if p != b'' and p != b'\n':
                    try:
                        p = p.rstrip(b'\n')
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
                        elif status_msg.status == firmware.status.status_enum.ACK:
                            if (last_line):
                                test_success = 1
                            proceed = 1
                            print('.', end='')
                            sys.stdout.flush()
                            break
                        elif status_msg.status == firmware.status.status_enum.REJECT:
                            proceed = 0
                            break
                        else:
                            print(bcolors.WARNING + bcolors.BOLD +
                                  "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                            print(bcolors.WARNING +
                                  str(p, 'utf-8') + bcolors.ENDC)

                    except:
                        print(bcolors.WARNING + bcolors.BOLD +
                              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                        print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)

            if last_line:
                if test_success:
                    print(bcolors.OKGREEN + bcolors.BOLD +
                          "\nTEST 1 SUCCESS" + bcolors.ENDC)
                    break
                else:
                    sys.exit(bcolors.FAIL + bcolors.BOLD +
                             "TEST 1 FAILED" + bcolors.ENDC)

            if proceed == 1:
                packet = firmware.firmware_packet()
                packet.line.record_type = f.read(2)
                if(packet.line.record_type == "S5"):
                    last_line = 1
                packet.line.byte_count = int(f.read(2), 16)
                packet.line.address = int(f.read(4), 16)
                packet.line.data = (binascii.a2b_hex(
                    f.read(2*packet.line.byte_count-6)))
                packet.line.checksum = int(f.read(2), 16)
                checksum_data = b'\x4a\x4f\x42\x42' + b'\x00\x00' + \
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
                # print("\n[DEBUG MESSAGE]")
                # print(packet.line.address)
                # print(packet.line.data)
                # print(packet.SerializeToString())
                pass

            term.write(bytes([packet.ByteSize()]))
            term.write(packet.SerializeToString())

        print(bcolors.WARNING + bcolors.BOLD +
              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)

        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':

                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':

                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':

                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break

    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION2), "r") as f:
        print(bcolors.OKBLUE + bcolors.BOLD +
              "EXECUTING TEST 2" + bcolors.ENDC)
        last_line = 0
        crc = CrcSTM()
        checksum_data = 0
        proceed = 0
        first_message = 1
        test_success = 0
        packet = None
        while True:
            while True:
                p = term.readline()
                p = p.replace(b'\xff', b'')
                if p != b'' and p != b'\n':
                    try:
                        p = p.rstrip(b'\n')
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
                        elif status_msg.status == firmware.status.status_enum.ACK:
                            if (last_line):
                                test_success = 1
                            proceed = 1
                            print('.', end='')
                            sys.stdout.flush()
                            break
                        elif status_msg.status == firmware.status.status_enum.REJECT:
                            proceed = 0
                            break
                        else:
                            print(bcolors.WARNING + bcolors.BOLD +
                                  "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                            print(bcolors.WARNING +
                                  str(p, 'utf-8') + bcolors.ENDC)

                    except:
                        print(bcolors.WARNING + bcolors.BOLD +
                              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                        print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)

            if last_line:
                if test_success:
                    print(bcolors.OKGREEN + bcolors.BOLD +
                          "\nTEST 2 SUCCESS" + bcolors.ENDC)
                    break
                else:
                    sys.exit(bcolors.FAIL + bcolors.BOLD +
                             "TEST 2 FAILED" + bcolors.ENDC)

            if proceed == 1:
                packet = firmware.firmware_packet()
                packet.line.record_type = f.read(2)
                if(packet.line.record_type == "S5"):
                    last_line = 1
                packet.line.byte_count = int(f.read(2), 16)
                packet.line.address = int(f.read(4), 16)
                packet.line.data = (binascii.a2b_hex(
                    f.read(2*packet.line.byte_count-6)))
                packet.line.checksum = int(f.read(2), 16)
                checksum_data = b'\x4a\x4f\x42\x42' + b'\x00\x00' + \
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

                n = random.randint(0, 15)

                if n == 7:
                    print(bcolors.WARNING + bcolors.BOLD +
                          "\n[A COMMUNICATION ERROR HAS BEEN ADDED]\n" + bcolors.ENDC)

                packet.checksum = crc.calc(checksum_data)
                f.read(1)
            else:
                # print("\n[DEBUG MESSAGE]")
                # print(packet.line.address)
                # print(packet.line.data)
                # print(packet.SerializeToString())
                pass

            term.write(bytes([packet.ByteSize()]))
            term.write(packet.SerializeToString())

        print(bcolors.WARNING + bcolors.BOLD +
              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)

        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break

    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION3), "r") as f:
        print(bcolors.OKBLUE + bcolors.BOLD +
              "EXECUTING TEST 3" + bcolors.ENDC)
        last_line = 0
        crc = CrcSTM()
        checksum_data = 0
        proceed = 0
        first_message = 1
        test_success = 0
        packet = None
        while True:
            while True:
                p = term.readline()
                p = p.replace(b'\xff', b'')
                if p != b'' and p != b'\n':
                    try:
                        p = p.rstrip(b'\n')
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
                        elif status_msg.status == firmware.status.status_enum.ACK:
                            if (last_line):
                                test_success = 1
                            proceed = 1
                            print('.', end='')
                            sys.stdout.flush()
                            break
                        elif status_msg.status == firmware.status.status_enum.REJECT:
                            proceed = 0
                            break
                        else:
                            print(bcolors.WARNING + bcolors.BOLD +
                                  "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                            print(bcolors.WARNING +
                                  str(p, 'utf-8') + bcolors.ENDC)

                    except:
                        print(bcolors.WARNING + bcolors.BOLD +
                              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                        print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)

            if last_line:
                if test_success:
                    print(bcolors.OKGREEN + bcolors.BOLD +
                          "\nTEST 3 SUCCESS" + bcolors.ENDC)
                    break
                else:
                    sys.exit(bcolors.FAIL + bcolors.BOLD +
                             "TEST 3 FAILED" + bcolors.ENDC)

            if proceed == 1:
                packet = firmware.firmware_packet()
                packet.line.record_type = f.read(2)
                if(packet.line.record_type == "S5"):
                    last_line = 1
                packet.line.byte_count = int(f.read(2), 16)
                packet.line.address = int(f.read(4), 16)
                packet.line.data = (binascii.a2b_hex(
                    f.read(2*packet.line.byte_count-6)))
                packet.line.checksum = int(f.read(2), 16)
                checksum_data = b'\x4a\x4f\x42\x42' + b'\x00\x00' + \
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
                # print("\n[DEBUG MESSAGE]")
                # print(packet.line.address)
                # print(packet.line.data)
                # print(packet.SerializeToString())
                pass

            term.write(bytes([packet.ByteSize()]))
            term.write(packet.SerializeToString())

        print(bcolors.WARNING + bcolors.BOLD +
              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)

        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break

    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION4), "r") as f:
        print(bcolors.OKBLUE + bcolors.BOLD +
              "EXECUTING TEST 4" + bcolors.ENDC)
        last_line = 0
        crc = CrcSTM()
        checksum_data = 0
        proceed = 0
        first_message = 1
        test_success = 0
        packet = None
        while True:
            while True:
                p = term.readline()
                p = p.replace(b'\xff', b'')
                if p != b'' and p != b'\n':
                    try:
                        p = p.rstrip(b'\n')
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
                        elif status_msg.status == firmware.status.status_enum.ACK:
                            if (last_line):
                                test_success = 1
                            proceed = 1
                            print('.', end='')
                            sys.stdout.flush()
                            break
                        elif status_msg.status == firmware.status.status_enum.REJECT:
                            proceed = 0
                            break
                        else:

                            print(bcolors.WARNING + bcolors.BOLD +
                                  "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                            print(bcolors.WARNING +
                                  str(p, 'utf-8') + bcolors.ENDC)

                    except:
                        print(bcolors.WARNING + bcolors.BOLD +
                              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)
                        print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)

            if last_line:
                if test_success:
                    print(bcolors.OKGREEN + bcolors.BOLD +
                          "\nTEST 4 SUCCESS" + bcolors.ENDC)
                    break
                else:
                    sys.exit(bcolors.FAIL + bcolors.BOLD +
                             "TEST 4 FAILED" + bcolors.ENDC)

            if proceed == 1:
                packet = firmware.firmware_packet()
                packet.line.record_type = f.read(2)
                if(packet.line.record_type == "S5"):
                    last_line = 1
                packet.line.byte_count = int(f.read(2), 16)
                packet.line.address = int(f.read(4), 16)
                packet.line.data = (binascii.a2b_hex(
                    f.read(2*packet.line.byte_count-6)))
                packet.line.checksum = int(f.read(2), 16)
                checksum_data = b'\x4a\x4f\x42\x42' + b'\x00\x00' + \
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
                # print("\n[DEBUG MESSAGE]")
                # print(packet.line.address)
                # print(packet.line.data)
                # print(packet.SerializeToString())
                pass

            term.write(bytes([packet.ByteSize()]))
            term.write(packet.SerializeToString())

        print(bcolors.WARNING + bcolors.BOLD +
              "\n[SATELITE RETURN MESSAGE]" + bcolors.ENDC)

        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break

        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        while True:
            p = term.readline()
            p = p.replace(b'\xcc', b'')
            p = p.replace(b'\xff', b'')
            if p != b'' and p != b'\n':
                print(bcolors.WARNING + str(p, 'utf-8') + bcolors.ENDC)
                break
        sys.exit(bcolors.OKGREEN + bcolors.BOLD +
                 "ALL TESTS ARE OK" + bcolors.ENDC)
