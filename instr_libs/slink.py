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
                        baudrate=921600,
                        timeout=2)
       
    dev.flushInput()
    dev.flushOutput()
    dev.write(('*VER\r').encode())
    time.sleep(1)
    print('response: '.format(dev.readline().decode()))

    
    
    
    
    dev.close()