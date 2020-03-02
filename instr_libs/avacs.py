# -*- coding: utf-8 -*-
"""
Modules for controlling Laseroptik AVACS beam attenuator.

Created on Tue Feb 11 10:42:10 2020
@author: ericmuckley@gmail.com
"""

import serial
from serial.tools import list_ports


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
            avacs['outbox'].append('Attenuator connected.')
            avacs['angle'].setEnabled(True)
            avacs['address'].setEnabled(False)
            avacs['curr_angle'].setEnabled(True)
            avacs['dev'].write('MR\r'.encode())
        except:  # serial.SerialException:
            avacs['outbox'].append('Attenuator could not connect.')
            avacs['angle'].setEnabled(False)
            avacs['address'].setEnabled(True)
            avacs['dev'] = None
            avacs['on'].setChecked(False)
            avacs['curr_angle'].setEnabled(False)
            avacs['curr_angle'].setText('---')
    if not avacs['on'].isChecked():
        try:
            avacs['dev'].close()
        except AttributeError:
            pass
        avacs['dev'] = None
        avacs['outbox'].append('Attenuator closed.')
        avacs['angle'].setEnabled(False)
        avacs['address'].setEnabled(True)
        avacs['on'].setChecked(False)
        avacs['curr_angle'].setEnabled(False)
        avacs['curr_angle'].setText('---')


def set_now(avacs):
    """Set angle of the beam attenuator."""
    position = round(avacs['angle'].value(), 1)
    pos_str = str(position).replace('.', '')
    avacs['outbox'].append(
            'Setting attenuator to {} degrees...'.format(position))
    avacs['dev'].write(('A'+pos_str+'\r').encode())
    avacs['outbox'].append('Attenuator set.')    



def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]



def response_to_angle(dev):
    """Get AVACS response and convert it to the current angle."""
    message = dev.readline().decode()
    angle = (int(float(message.split(';')[2])/10))
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
