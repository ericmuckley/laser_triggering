# -*- coding: utf-8 -*-
"""

MOdule for controlling the Marzhauser MCL-3 stage controller.
Note: the Marzhauser ECO-STEP controller uses a different set of
serial commands. For the ECO-STEP, test communication using:
dev.write(('?ver\r\r').encode())
print(dev.readline().decode())


Created on Mon Feb  3 15:39:10 2020
@author: ericmuckley@gmail.com

"""

import serial
import numpy as np
from serial.tools import list_ports


def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]

#print_ports()

address = 'COM22'



def get_x_pos(dev):
    """Get current X position of stage."""
    dev.write(('UC\r\r').encode())
    return int(dev.readline().decode())

def get_y_pos(dev):
    """Get current Y position of stage."""
    dev.write(('UD\r\r').encode())
    return int(dev.readline().decode())

def get_z_pos(dev):
    """Get current Z position of stage."""
    dev.write(('UE\r\r').encode())
    return int(dev.readline().decode())

def get_pos(dev):
    """Get absolute position of stage."""
    x = get_x_pos(dev)
    y = get_y_pos(dev)
    z = get_z_pos(dev)
    return (x, y, z)

def get_status(dev):
    """Get device status."""
    dev.write(('UF\r\r').encode())
    return dev.readline().decode()




#print('abs. position: {}'.format(get_abs_pos(dev)))


#dev.write(('U\07r\rU\000\rU\r\r').encode())
#dev.write(('UB\r\r').encode())
#print('reading: {}'.format(dev.readline().decode()))


def move(dev):
    """Move stage to absolute position."""
    #dev.write(('U\07r\rU\000\rU\r\r').encode())
    #dev.write(('U\000\r\r').encode())
    
    
    dev.write(('UG\r\r').encode())
    dev.write(('UI50\r\r').encode())
    dev.write(('UP\r\r').encode())

#move(dev)
    


dev = serial.Serial(port=address, timeout=2,
                    stopbits=serial.STOPBITS_TWO)



# clear stage
#dev.write(('U\000\r\r').encode())
#dev.write(('U\010\r\r').encode())



'''
#dev.write(('U\000\r\r').encode())
#dev.write(('U\010\r\r').encode())
dev.write(('U7v\r\r').encode())
dev.write(('U00333\r\r').encode())
dev.write(('U01222\r\r').encode())
dev.write(('UP\r\r').encode())
'''


dev.write(('U\07v\r\r').encode())
dev.write(('U02\r\r').encode())
dev.write(('U14\r\r').encode())



dev.write(('UC\r\r').encode())
print('x pos '+dev.readline().decode())
dev.write(('UD\r\r').encode())
print('y pos '+dev.readline().decode())



print('position: {}'.format(get_pos(dev)))


print('Device status: {}'.format(get_status(dev)))



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
UD\r
"""