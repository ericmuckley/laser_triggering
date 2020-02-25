# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 15:39:10 2020

@author: a6q
"""
import time
import serial
import numpy as np
from serial.tools import list_ports

import io


def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]


print_ports()

address = 'COM17'
dev = serial.Serial(port=address,
                    baudrate=9600,
                    timeout=2,
                    write_timeout=0.5,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE)


sio = io.TextIOWrapper(io.BufferedRWPair(dev, dev))
sio.write(str(r'?ver\r'))
sio.flush()
message = sio.readline()
print(message)


dev.write((r'?ver\r').encode())

dev.flushOutput()
dev.flushInput()
dev.write((r'?ver\r').encode())
print(dev.readline())

#dev.write(('?pos\r').encode())
#print(dev.read(1))
#print('-------------------')

print(dev.isOpen())
dev.close()

