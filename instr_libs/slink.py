# -*- coding: utf-8 -*-
"""

Module for controlling the Gentech S-Link photometer.

Created on Mon Mar  2 15:34:06 2020
@author: ericmuckley@gmail.com
"""

import codecs
import time
import serial
import numpy as np
from serial.tools import list_ports

decode_hex = codecs.getdecoder('hex_codec')

def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]




range_dict = {
    '00': '1 picowatt or picojoule',
    '01': '3 picowatts or picojoules',
    '02': '10 picowatts or picojoules',
    '03': '30 picowatts or picojoules',
    '04': '100 picowatts or picojoules',
    '05': '300 picowatts or picojoules',
    '06': '1 nanowatt or nanojoule',
    '07': '3 nanowatts or nanojoules',
    '08': '10 nanowatts or nanojoules',
    '09': '30 nanowatts or nanojoules',
    '10': '100 nanowatts or nanojoules',
    '11': '300 nanowatts or nanojoules',
    '12': '1 microwatt or microjoule',
    '13': '3 microwatts or microjoules',
    '14': '10 microwatts or microjoules',
    '15': '30 microwatts or microjoules',
    '16': '100 microwatts or microjoules',
    '17': '300 microwatts or microjoules',
    '18': '1 milliwatt or millijoule',
    '19': '3 milliwatts or millijoules',
    '20': '10 milliwatts or millijoules',
    '21': '30 milliwatts or millijoules',
    '22': '100 milliwatts or millijoules',
    '23': '300 milliwatts or millijoules',
    '24': '1 Watt or Joule',
    '25': '3 watts or joules',
    '26': '10 watts or joules',
    '27': '30 watts or joules',
    '28': '100 watts or joules',
    '29': '300 watts or joules',
    '30': '1 kilowatt or kilojoule',
    '31': '3 kilowatts or kilojoules',
    '32': '10 kilowatts or kilojoules',
    '33': '30 kilowatts or kilojoules',
    '34': '100 kilowatts or kilojoules',
    '35': '300 kilowatts or kilojoules',
    '36': '1 megawatt or megajoule',
    '37': '3 megawatts or megajoules',
    '38': '10 megawatts or megajoules',
    '39': '30 megawatts or megajoules',
    '40': 'megawatts or megajoules',
    '41': '300 megawatts or megajoules'}



def read(dev):
    """Read communication from a serial device."""
    return dev.read(100).decode()


def version_number(dev):
    """Read version number from the photometer."""
    dev.write('*VER'.encode())
    return dev.readline().decode()



def get_status(dev):
    """Read status of the photometer settings."""
    dev.write('*ST1'.encode())
    s = dev.read(150).decode().split('\r\n')
    wavelength = s[0]#[2:]
    print(wavelength)
    #wavelength = bytes.fromhex(s).decode('ascii')
    return s, wavelength



if __name__ == '__main__':

    #print_ports()
    
    address = 'COM25'
    
    dev = serial.Serial(port=address, baudrate=921600, timeout=2)

    print('Version number: {}'.format(version_number(dev)))

    scale = '02'

    dev.write('*SS1001'.encode())
    dev.write('*VNM'.encode())
    dev.write('*CA1'.encode())
    dev.write('*CV1'.encode())
    dev.write(('*SC1'+scale).encode())
    print('channel 1 intensity:')
    print(dev.readline().decode().split(':')[1])



    dev.close()







