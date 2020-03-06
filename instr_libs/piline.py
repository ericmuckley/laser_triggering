# -*- coding: utf-8 -*-

"""
This module contains methods for controlling the PI C-867 PILine
roation controller. DIP switches on the back of the PI C-867 unit
should be set before powering the unit so that the controller
address is 1. DIP switch settings:
1 - 4: ON
5 - 8: OFF

Created on Wed Mar  4 11:38:43 2020
@author: ericmuckley@gmail.com
"""


import time
import serial
import numpy as np


def enable_piline(piline, enable):
    """Enable/disable GUI widgets related to the PI
    PILine C-1867 rotation controller."""
    piline['address'].setEnabled(not enable)
    items = ['set', 'display', 'seq', 'initial',
             'set_now', 'final', 'steps', 'preview']
    [piline[i].setEnabled(enable) for i in items]



def piline_on(piline):
    """Run this when piline checkbox is checked/unchecked."""
    if piline['on'].isChecked():
        try:
            dev = serial.Serial(port=piline['address'].text(),
                                baudrate=115200, timeout=2)
            piline['dev'] = dev
            initialize(piline)
            piline['outbox'].append('PI C-867 connected.')
            enable_piline(piline, True)
            piline['outbox'].verticalScrollBar().setValue(99999999)
        except:
            enable_piline(piline, False)
            piline['outbox'].append('PI C-867 could not connect.')
            piline['dev'] = None
            piline['on'].setChecked(False)
    if not piline['on'].isChecked():
        try:
            piline['dev'].close()
        except AttributeError:
            pass
        piline['outbox'].append('PI C-867 closed.')
        enable_piline(piline, False)
        piline['dev'] = None
        piline['display'].setText('---')
        piline['on'].setChecked(False)


def initialize(piline):
    """Initialize the stage and get some operating parameters."""
    # get reference point and wait until its finished
    piline['outbox'].append('Please wait while C-867 stage initializes...')
    turn_on_servo(piline['dev'], on=True)
    piline['dev'].write(('FRF 1\n').encode())
    time.sleep(6)
    # read stage information
    piline['outbox'].append(
        'Controller ID: {}'.format(get_id(piline['dev'])))
    piline['outbox'].append(
        'stage type: {}'.format(get_stage_type(piline['dev'])))
    piline['outbox'].append('servo on: {}'.format(check_servo(piline['dev'])))
    # display position value 
    piline['dev'].write(('POS?\n').encode())
    pos = piline['dev'].readline().decode()  
    pos = float(pos.split('=')[1])
    piline['display'].setText(str(pos))    


def move(piline):
    """Move the stage to a position designated on the GUI."""
    piline['set_now'].setEnabled(False)
    # get currently set position
    set_pos = float(piline['set'].value())
    piline['display'].setText('moving')
    piline['outbox'].append('Moving rotation stage to {}...'.format(set_pos))
    # begin moving toward new set position
    piline['dev'].write(('MOV 1 '+str(set_pos)+'\n').encode())
    # get current position
    curr_pos = get_position_float(piline)
    # wait until current position = set position
    while round(set_pos) != round(curr_pos):
        time.sleep(0.5)
        curr_pos = get_position_float(piline)
    time.sleep(0.5)
    # display new position value 
    piline['display'].setText(str(get_position_float(piline)))
    piline['outbox'].append('Stage rotation complete.')
    piline['set_now'].setEnabled(True)
    piline['outbox'].verticalScrollBar().setValue(99999999)

def get_position_float(piline):
    """Get current positoin of stage as a float."""
    piline['dev'].write(('POS?\n').encode())
    pos = piline['dev'].readline().decode()
    pos = float(pos.split('=')[1])
    return pos


def preview_angles(piline):
    """Get preview of angles to sample."""
    angles = get_angles(piline)
    piline['outbox'].append('Angles to sample in degrees:')
    piline['outbox'].append(str(angles))
    piline['outbox'].verticalScrollBar().setValue(99999999)
    

def get_angles(piline):
    """Get angles to sample."""
    angles = np.linspace(
        piline['initial'].value(),
        piline['final'].value(),
        piline['steps'].value()+1)
    return angles



def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(serial.tools.list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]

def get_id(dev):
    """Get ID of device."""
    dev.write(('*IDN?\n').encode())
    return dev.readline().decode()

def get_position(dev):
    """Get current real position."""
    dev.write(('POS?\n').encode())
    return dev.readline().decode()   

def get_stage_type(dev):
    """Get the stage type connected to the controller."""
    dev.write(('CST?\n').encode())
    return dev.readline().decode() 

def get_servo_mode(dev):
    """Get servomotor mode."""
    dev.write(('SVO?\n').encode())
    return bool(int(dev.readline().decode().split('=')[1]))

def turn_on_servo(dev, on=True):
    """Turn on or off the servo motor."""
    dev.write(('SVO 1 '+str(int(on))+'\n').encode())

def get_motion_lims(dev):
    """Get min and max motion limits of the stage."""
    dev.write(('TMN?\n').encode())
    min_lim = dev.readline().decode().split('=')[1]
    dev.write(('TMX?\n').encode())
    max_lim = dev.readline().decode().split('=')[1]
    dev.write(('LIM?\n').encode())
    lim_switches = dev.readline().decode().split('=')[1]
    return (min_lim, max_lim, lim_switches)

def check_servo(dev):
    """Check whether servo motor is on."""
    dev.write(('SVO?\n').encode())
    return bool(int(dev.readline().decode().split('=')[1]))

def get_error(dev):
    """Return error of the device.""" 
    dev.write(('ERR?\n').encode())
    return dev.readline().decode()

def get_reference_mode(dev):
    """Get reference mode of the device."""
    dev.write(('RON?\n').encode())
    return dev.readline().decode()

def get_reference_result(dev):
    """Get result of reference query."""
    dev.write(('FRF? 1\n').encode())
    return dev.readline().decode()

def initialize_stage(dev):
    """Initialize the stage and get some operating parameters."""
    turn_on_servo(dev, on=True)
    # read stage information
    print('Controller ID: {}'.format(get_id(dev)))
    print('stage type: {}'.format(get_stage_type(dev)))
    print('current position: {}'.format(get_position(dev)))
    print('servo on: {}'.format(check_servo(dev)))
    print('reference mode: {}'.format(get_reference_mode(dev)))
    # get reference point and wait until its finished
    dev.write(('FRF 1\n').encode())
    time.sleep(6)
    ref_result = bool(int(get_reference_result(dev).split('=')[1]))
    print('Reference successful: {}'.format(ref_result))
    print('Stage configured successfully.')


if __name__ == '__main__':


    address = 'COM24'
    dev = serial.Serial(port=address, baudrate=115200, timeout=2)
    initialize_stage(dev)

    dev.write(('MOV 1 360\n').encode())

    time.sleep(5)


    turn_on_servo(dev, on=False)

    print('current position: {}'.format(get_position(dev)))

    print('error code: {}'.format(get_error(dev)))
    dev.close()

