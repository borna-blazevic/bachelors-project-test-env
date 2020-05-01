#!/usr/bin/env python


from subprocess import Popen, PIPE, STDOUT
import sys
import re
import time
import os
import binascii
import crcmod
from proto.firmware_package_pb2 import *

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

FIRMWARE_LOCATION = "./firmware/firmware.srec"

if(len(sys.argv) < 2):
    print("USING DEFAULT LOCATION \"" , FIRMWARE_LOCATION, "\"")


p1 = Popen('qemu-system-arm -machine lm3s6965evb -serial pty -kernel output/combined.bin -s',
          shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)

stdout_data = p1.stdout.readline()
pty = re.search("/(.+?)[0-9]+", stdout_data.decode("utf-8")).group(0)


print("QEMU emulator avaliable at: ", pty)
fileSize=os.path.getsize(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION))
print("Firmware size: ", fileSize)


with open(pty, "wb+", buffering=0) as term:
    print(term.readline().decode())
    sys.stdout.flush()
    term.write(fileSize.to_bytes(4,byteorder="little",signed=False))
    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION), "r") as f:
        print("Executing firmware upgrade")

        
        while True:
            packet = send_packet()
            packet.line.record_type = f.read(2)
            if(not packet.line.record_type):
                break
            packet.line.byte_count = f.read(2)
            if(not packet.line.byte_count):
                break
            packet.line.address = f.read(4)
            if(not packet.line.address):
                break
            packet.line.data = f.read(2*int(packet.line.byte_count, 16)-6)
            if(not packet.line.data):
                break
            packet.line.checksum = f.read(2)
            if(not packet.line.checksum):
                break

            print(packet.line.SerializeToString())
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

        
