# -*- coding: utf-8 -*-
"""

Module for controlling the Gentech S-Link photometer.

Created on Mon Mar  2 15:34:06 2020
@author: ericmuckley@gmail.com
"""

import time
import serial
import numpy as np
from serial.tools import list_ports



def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]





if __name__ == '__main__':
    
    
    print_ports()
    
    address = 'COM25'
    dev = serial.Serial(port=address,
                        baudrate=9600,#921600,#115200,#,
                        timeout=1)

    dev.write(('*VER').encode())
    time.sleep(1)
    
    dev.flushInput()
    dev.flushOutput()
    
    print('response: '.format(dev.readline()))#.decode()))
    print('response: '.format(dev.read(10)))#.decode()))
    
    

    
    
    
    
    dev.close()