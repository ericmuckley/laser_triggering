# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 15:39:10 2020

@author: a6q
"""

import serial
import numpy as np
from serial.tools import list_ports

import io

def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]

#print_ports()

address = 'COM22'


#stage = 'ECO-STEP'
stage = 'MCL'

dev = serial.Serial(port=address, timeout=2,
                    stopbits=serial.STOPBITS_TWO)


if stage not in ['ECO-STEP', 'MCL']:
    print('Incorrect stage name.')
    dev = serial.Serial()


if stage == 'ECO-STEP':
    dev.write(('?ver\r\r').encode())
    print(dev.readline().decode())


if stage == 'MCL':
    dev.write(('UC\r\r').encode())
    print(dev.readline().decode())



dev.close()




"""
From Alex Strasser's LabVIEW program for controlling the MCL
visa open
visa clear buffers

visa write lines:
U 0
U\010\r
U\07v\rU\000\r
visa read

visa write lines:
U 0
U\010\r
U\07v\rU\011\r
visa read

# move absolute (home?)
visa write lines:
U\07r\rU\000\rU
U\000\r
U\07r\rU\010\rU
U\010\r

#read position
visa write lines:
# x position
UC\r
# y position
CD\r
"""