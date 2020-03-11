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
    avacs['display'].setText('moving')
    # get set position from GUI
    setpoint = round(avacs['set'].value(), 1)
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
    avacs['outbox'].append('Attenuator set.')   
    avacs['set_now'].setEnabled(True)



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
