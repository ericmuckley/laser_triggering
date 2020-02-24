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
            avacs['set_now'].setEnabled(True)
            avacs['address'].setEnabled(False)
            avacs['dev'].write('MR\r'.encode())
        except serial.SerialException:
            avacs['outbox'].append('Attenuator could not connect.')
            avacs['angle'].setEnabled(False)
            avacs['set_now'].setEnabled(False)
            avacs['address'].setEnabled(True)
            avacs['dev'] = None
            avacs['on'].setChecked(False)
    if not avacs['on'].isChecked():
        try:
            avacs['dev'].close()
        except AttributeError:
            pass
        avacs['dev'] = None
        avacs['outbox'].append('Attenuator closed.')
        avacs['angle'].setEnabled(False)
        avacs['set_now'].setEnabled(False)
        avacs['address'].setEnabled(True)
        avacs['on'].setChecked(False)


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



if __name__ == '__main__':
    
    print_ports()
    address = 'COM5'
    position = 40.0

    dev = serial.Serial(port=address,
                        baudrate=19200,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=2)
    
    #dev.write('MM\r'.encode())  # manual mode
    #dev.write('MA\r'.encode())  # analog mode
    
    pos_str = str(position).replace('.', '')
    dev.write('MR\r'.encode())  # remote mode
    dev.write(('A'+pos_str+'\r').encode())

    dev.close()    
