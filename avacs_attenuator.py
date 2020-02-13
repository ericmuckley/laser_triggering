# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 10:42:10 2020

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





print_ports()

address = 'COM11'


dev = serial.Serial(port=address, baudrate=9600, timeout=2)

dev.write(('mhRS\n').encode('utf-8'))
print(dev.readline())


dev.close()




'''



# set target location

tar_loc = (100, 100)
tar_loc_str = 'GR {} {}\r'.format(tar_loc[0], tar_loc[1])



dev.write(('L 100\r').encode('utf-8'))
'''