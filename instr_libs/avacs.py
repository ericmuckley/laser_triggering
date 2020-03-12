# -*- coding: utf-8 -*-
"""
Modules for controlling Laseroptik AVACS beam attenuator.

Created on Tue Feb 11 10:42:10 2020
@author: ericmuckley@gmail.com
"""

import time
import serial
import numpy as np
from serial.tools import list_ports

def enable_avacs(avacs, enabled):
    """Enable/disable GUI objects."""
    for i in avacs:
        if i not in ['on', 'address', 'dev', 'outbox']:
            avacs[i].setEnabled(enabled)
    avacs['address'].setEnabled(not enabled)
    

def avacs_on(avacs):
    "Run this when Laseroptik beam attenuator checkbox is checked."""
    if avacs['on'].isChecked():
        try:
            dev = serial.Serial(port=avacs['address'].text(),
                                baudrate=19200,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                timeout=2)
            avacs['dev'] = dev
            # set unit in remote mode
            avacs['dev'].write('MR\r'.encode())
            enable_avacs(avacs, True)
            avacs['outbox'].append('Attenuator connected.')
            set_now(avacs)
        except:  # serial.SerialException:
            avacs['outbox'].append('Attenuator could not connect.')
            avacs['outbox'].append('Try setting *Remote* mode on the unit.')
            avacs['dev'] = None
            avacs['on'].setChecked(False)
            avacs['display'].setText('---')
            enable_avacs(avacs, False)
    if not avacs['on'].isChecked():
        try:
            avacs['dev'].close()
        except AttributeError:
            pass
        avacs['dev'] = None
        avacs['outbox'].append('Attenuator closed.')
        avacs['on'].setChecked(False)
        avacs['display'].setText('---')
        enable_avacs(avacs, False)


def set_now(avacs):
    """Set angle of the beam attenuator."""
    avacs['set_now'].setEnabled(False)
    avacs['set_percent_now'].setEnabled(False)
    avacs['display'].setText('moving')
    # get set position from GUI
    setpoint = round(avacs['set'].value(), 1)
    avacs['set_percent'].setValue(angle_to_percent(setpoint))
    pos_str = str(setpoint).replace('.', '')
    avacs['setpoint_str'] = pos_str
    # write new position to unit
    avacs['dev'].write(('A'+pos_str+'\r').encode())
    avacs['outbox'].append(
            'Setting attenuator to {} degrees...'.format(setpoint))
    
    # wait until angle reaches the setpoint
    current_angle = get_current_angle(avacs)
    while round(current_angle) != round(setpoint):
        time.sleep(1)
        current_angle = get_current_angle(avacs)
    avacs['display'].setText(str(current_angle))
    avacs['display_percent'].setText(str(angle_to_percent(current_angle)))
    avacs['outbox'].append('Attenuator set.')   
    avacs['set_now'].setEnabled(True)
    avacs['set_percent_now'].setEnabled(True)


def set_percent_now(avacs):
    """Set percent power of the beam attentuator."""
    avacs['set'].setValue(percent_to_angle(avacs['set_percent'].value()))
    set_now(avacs)
    

def get_sweep(avacs):
    """Get beam powers to sweep for the experimental sequence."""
    sweep = np.linspace(
        avacs['initial'].value(),
        avacs['final'].value(),
        avacs['steps'].value()+1)
    return sweep


def get_current_angle(avacs):
    """Get current angle of AVACS."""
    while True:
        try:
            avacs['dev'].write(('A'+avacs['setpoint_str']+'\r').encode())
            angle_raw = avacs['dev'].read(11).decode()
            angle = round(float(angle_raw.split(';')[2])/10, 1)
            break
        except ValueError:
            time.sleep(1)
    return angle




def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]



def angle_to_percent(angle):
    """Convert attenuator angle to percent power with logistic function."""
    x0 = 28.1336
    k = -0.288186
    L = 0.994308 
    return 100 * (L / (1 + np.exp(-k*(angle-x0))))


def percent_to_angle(percent):
    """Convert attenuator percent power to angle with logistic function."""
    x0 = 28.1336
    k = -0.288186
    L = 0.994308 
    return x0 - np.log(100*L/percent - 1)/k








if __name__ == '__main__':
    
    #print_ports()
    address = 'COM17'
    position = 38.0

    dev = serial.Serial(port=address,
                        baudrate=19200,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=2)

    
    pos_str = str(position).replace('.', '')
        
    # set in manual mode
    # dev.write('MM\r'.encode()) 
    # set in analog mode
    # dev.write('MA\r'.encode())  
    # set in remote mode
    dev.write('MR\r'.encode()) 
    # set the angle
    dev.write(('A'+pos_str+'\r').encode())

    dev.write('I\r'.encode())
    print(dev.readline())
    
    dev.write('R\r'.encode())
    message = dev.read(11).decode()
    print(int(float(message.split(';')[2])/10))

    dev.close()    
