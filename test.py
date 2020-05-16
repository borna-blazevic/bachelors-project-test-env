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

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

FIRMWARE_LOCATION = "./firmware/firmware.srec"

if(len(sys.argv) < 2):
    print("USING DEFAULT LOCATION \"" , FIRMWARE_LOCATION, "\"")


p1 = Popen('qemu-system-arm -machine lm3s6965evb -serial pty -kernel output/combined.bin -s -S',
          shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)

stdout_data = p1.stdout.readline()
pty = re.search("/(.+?)[0-9]+", stdout_data.decode("utf-8")).group(0)


print("QEMU emulator avaliable at: ", pty)
fileSize=os.path.getsize(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION))
print("Firmware size: ", fileSize)


with open(pty, "wb+", buffering=0) as term:
    sys.stdin.readline()
    # print(term.readline().decode())
    # sys.stdout.flush()
    #term.write(fileSize.to_bytes(4,byteorder="little",signed=False))
    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION), "r") as f:
        print("Executing firmware upgrade")

        while True:
            srec_line = srec_line()
            srec_line.record_type = f.read(2)
            if(not srec_line.record_type):
                break
            srec_line.byte_count = int(f.read(2), 16)
            if(not srec_line.byte_count):
                break
            srec_line.address = int(f.read(4), 16)
            srec_line.data = binascii.a2b_hex(
            f.read(2*srec_line.byte_count-6))
            if(not srec_line.data):
                break
            srec_line.checksum = int(f.read(2), 16)
            if(not srec_line.checksum):
                break

            term.write(bytes([srec_line.ByteSize()]))
            term.write(srec_line.SerializeToString())
            print(term.read(1))
            print(term.readline().decode(), end='')

            while True:
                print(term.readline().decode(), end='')
            # print(term.readline().decode(), end='')
            # print(term.readline().decode(), end='')
            # print(term.readline().decode(), end='')
            # print(term.readline().decode(), end='')
            
            # term.write(byte)
            # res = term.readline().decode()
            # if(not (res.rstrip() =='Byte recieved' or res.rstrip() == 'Bytes written')):
            #     print("Error")
            #     print(res.rstrip())
            #     sys.stdout.flush()
            # else:
            #     sys.stdout.flush()
            byte = f.read(1)
    print("Finished sending firmware!")
    while True:
        print(term.readline().decode(), end='')
        sys.stdout.flush()

        
