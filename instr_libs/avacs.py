# -*- coding: utf-8 -*-
"""
Modules for controlling Laseroptik AVACS beam attenuator.

Created on Tue Feb 11 10:42:10 2020
@author: ericmuckley@gmail.com
"""

import time
import serial
from serial.tools import list_ports


def enable_avacs(avacs, enabled):
    """Enable/disable GUI objects."""
    items = ['set', 'display', 'set_now']
    [avacs[i].setEnabled(enabled) for i in items]
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
            enable_avacs(avacs, True)
            avacs['outbox'].append('Attenuator connected.')
            set_now(avacs)
            # set unit in remote mode
            avacs['dev'].write('MR\r'.encode())
        except:  # serial.SerialException:
            avacs['outbox'].append('Attenuator could not connect.')
            avacs['dev'] = None
            avacs['on'].setChecked(False)
            avacs['curr_angle'].setText('---')
            enable_avacs(avacs(avacs, False))
    if not avacs['on'].isChecked():
        try:
            avacs['dev'].close()
        except AttributeError:
            pass
        avacs['dev'] = None
        avacs['outbox'].append('Attenuator closed.')
        avacs['on'].setChecked(False)
        avacs['curr_angle'].setText('---')
        enable_avacs(avacs, False)


def set_now(avacs):
    """Set angle of the beam attenuator."""
    avacs['set_now'].setEnabled(False)
    avacs['display'].setText('moving')
    # get set position rom GUI
    position = round(avacs['angle'].value(), 1)
    pos_str = str(position).replace('.', '')
    # write new position to unit
    avacs['dev'].write(('A'+pos_str+'\r').encode())
    avacs['outbox'].append(
            'Setting attenuator to {} degrees...'.format(position))
    time.sleep(2)
    # set new angle display on GUI
    get_current_angle(avacs)
    avacs['outbox'].append('Attenuator set.')   
    avacs['set_now'].setEnabled(True)



def get_current_angle(avacs):
    """Get current angle of AVACS."""
    avacs['dev'].write(('A'+pos_str+'\r').encode())
    angle_raw = avacs['dev'].read(11).decode()
    angle = round(float(angle_raw.split(';')[2])/10, 1)
    avacs['display'].setText(str(angle))
    return angle



def update_angle(avacs):
    """Update the current angle on the GUI."""
    position = round(avacs['angle'].value(), 1)
    pos_str = str(position).replace('.', '')
    avacs['dev'].write(('A'+pos_str+'\r').encode())
    message = avacs['dev'].read(11).decode()
    try:
        curr_angle = round(float(message.split(';')[2])/10, 1)
    except IndexError:
        curr_angle = '---'
    avacs['curr_angle'].setText(str(curr_angle))






def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]


if __name__ == '__main__':
    
    print_ports()
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

    # dev.write('I\r'.encode())
    # print(dev.readline())
    
    #dev.write('R\r'.encode())
    message = dev.read(11).decode()
    print(int(float(message.split(';')[2])/10))

    dev.close()    
