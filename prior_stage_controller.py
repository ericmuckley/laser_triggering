# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 15:39:10 2020

@author: a6q
"""

import serial
import numpy as np
from serial.tools import list_ports


def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]


def print_stage_info(dev):
    """Print a list of information about the stage setup."""
    dev.write(('?\r').encode('utf-8'))
    stage_info = str(dev.readline()).split(r'\r')
    print('--------------------------------')
    print('Peripherals information:')
    [print(info) for info in stage_info]
    print('--------------------------------')


#print_ports()

address = 'COM5'
dev = serial.Serial(port=address, timeout=2)

print_stage_info(dev)



# set target location
'''
tar_loc = (100, 100)
tar_loc_str = 'GR {} {}\r'.format(tar_loc[0], tar_loc[1])
dev.write((tar_loc_str).encode('utf-8'))
'''

dev.write(('L 100\r').encode('utf-8'))


dev.write(('M\r').encode('utf-8'))


# get current position
dev.write(('PS\r').encode('utf-8'))
curr_loc = str(dev.readline().decode())
print('Current position:')
print(curr_loc)


'''
# set speed to 50% on each axis
dev.write(('3X50\r').encode('utf-8'))
dev.write(('3Y50\r').encode('utf-8'))
dev.write(('3Z50\r').encode('utf-8'))


dev.write(('P\r').encode('utf-8'))
print(dev.readline().decode())
'''
dev.close()

