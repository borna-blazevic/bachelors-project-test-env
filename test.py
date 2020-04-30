#!/usr/bin/env python


from subprocess import Popen, PIPE, STDOUT
import sys
import re
import time
import os
import binascii

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

FIRMWARE_LOCATION = "./firmware/firmware.bin"

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
    with open(os.path.join(CURRENT_PATH, FIRMWARE_LOCATION), "rb") as f:
        print("Executing firmware upgrade")
        byte = f.read(1)
        while byte:
            term.write(byte)
            res = term.readline().decode()
            if(not (res.rstrip() =='Byte recieved' or res.rstrip() == 'Bytes written')):
                print("Error")
                print(res.rstrip())
                sys.stdout.flush()
            else:
                sys.stdout.flush()
            byte = f.read(1)
    print("Finished sending firmware!")
    while True:
        print(term.readline().decode(), end='')
        sys.stdout.flush()

        
