# -*- coding: utf-8 -*-
"""

Module for controlling the Marzhauser MCL-3 stage controller.
Note: the Marzhauser ECO-STEP controller uses a different set of
serial commands than the MCL-3. For the MCL-3, use commands in
this module.

For the ECO-STEP, test communication using:
dev.write(('?ver\r\r').encode())
print(dev.readline().decode())

# default scale for the MCL-3 stage is
# 4000 units == 1 cm

Created on Mon Feb  3 15:39:10 2020
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


def enable_stage(mcl, enabled):
    """Enable/disable GUI objects related to the MCL stage."""
    items = ['seq', 'set_x', 'set_y', 'grid_xf', 'show_x', 'show_y',
             'grid_yf', 'grid_xi', 'grid_yi', 'grid_xsteps', 'grid_ysteps',
             'preview_grid_cords', 'set_now']
    [mcl[i].setEnabled(enabled) for i in items]
    mcl['address'].setEnabled(not enabled)


def stage_on(mcl):
    "Run this function when MCL-3 stage checkbox is checked."""
    if mcl['on'].isChecked():
        try:
            dev = serial.Serial(
                    port=mcl['address'].text(),
                    timeout=1,
                    stopbits=serial.STOPBITS_TWO)
            mcl['dev'] = dev
            mcl['outbox'].append('Configuring Marzhauser MCL-3 stage...')
            clear_stage_buffer(dev)
            mcl['outbox'].append('Stage status: {}'.format(get_status(dev)))
            x, y = get_x_pos(mcl['dev']), get_y_pos(mcl['dev'])
            mcl['show_x'].setText(str(x))
            mcl['show_y'].setText(str(y))
            mcl['set_x'].setValue(float(x))
            mcl['set_y'].setValue(float(y))
            set_now(mcl)
            enable_stage(mcl, True)
            mcl['outbox'].append('Marzhauser MCL-3 stage connected.')
        except:
            mcl['outbox'].append('Stage could not connect.')
            mcl['outbox'].append('Make sure it is "auto" mode.')
            enable_stage(mcl, False)
            mcl['dev'] = None
            mcl['on'].setChecked(False)
            mcl['show_x'].setText('---')
            mcl['show_y'].setText('---')
            mcl['seq'].setChecked(False)
    if not mcl['on'].isChecked():
        try:
            mcl['dev'].close()
        except AttributeError:
            pass
        mcl['outbox'].append('Stage closed.')
        enable_stage(mcl, False)
        mcl['on'].setChecked(False)
        mcl['show_x'].setText('---')
        mcl['show_y'].setText('---')
        mcl['dev'] = None
        mcl['seq'].setChecked(False)



 
def set_now(mcl):
    """Set the stage to a new position."""
    mcl['busy'] = True
    mcl['set_now'].setEnabled(False)
    mcl['show_x'].setText('moving')
    mcl['show_y'].setText('moving')
    
    # get new user-defined coordinates from the GUI in centimeters
    new_x = round(mcl['set_x'].value(), 2)
    new_y = round(mcl['set_y'].value(), 2)
    mcl['outbox'].append('Moving stage to ({}, {})...'.format(new_x, new_y))
    
    # get current position of stage
    current_x = get_x_pos(mcl['dev'])
    current_y = get_y_pos(mcl['dev'])

    # move to new position 
    dx, dy = round(new_x-current_x, 2), round(new_y-current_y, 2)
    if dx != 0 or dy != 0:
        move_by(mcl['dev'], int(dx*4000), int(dy*4000))
        clear_stage_buffer(mcl['dev'])
        time.sleep(1)
        # wait until stage position has reached its setpoint
        while current_x != new_x or current_y != new_y:
            current_x = get_x_pos(mcl['dev'])
            current_y = get_y_pos(mcl['dev'])
            time.sleep(1)
    mcl['outbox'].append('Stage at {}'.format((current_x, current_y)))
    mcl['show_x'].setText(str(current_x))
    mcl['show_y'].setText(str(current_y))
    mcl['set_now'].setEnabled(True)
    mcl['busy'] = False



def get_grid(mcl):
    """Get grid coordinates from grid settings on GUI."""
    x_cords, y_cords = get_sweep_cords(mcl)
    grid_cords = np.array(np.meshgrid(x_cords, y_cords)).T.reshape(-1,2)
    return grid_cords


def get_sweep_cords(mcl):
    """Get X-Y coordinates to sweep accross during sequence."""
    x_cords = np.linspace(mcl['grid_xi'].value(),
                          mcl['grid_xf'].value(),
                          mcl['grid_xsteps'].value()+1)
    y_cords = np.linspace(mcl['grid_yi'].value(),
                          mcl['grid_yf'].value(),
                          mcl['grid_ysteps'].value()+1)
    return x_cords, y_cords


def get_x_pos(dev):
    """Get current X position of stage."""
    clear_stage_buffer(dev)
    while True:
        try:
            dev.write(('UC\r\r').encode())
            x_pos = dev.readline().decode()
            x_pos = round(float(x_pos)/4000, 2)
            break
        except ValueError:
            time.sleep(1)
    return x_pos


def get_y_pos(dev):
    """Get current Y position of stage."""
    clear_stage_buffer(dev)
    while True:
        try:
            dev.write(('UD\r\r').encode())
            y_pos = dev.readline().decode()
            y_pos = round(float(y_pos)/4000, 2)
            break
        except ValueError:
            time.sleep(1)
    return y_pos
    


def clear_stage_buffer(dev):
    """Clear the input/output buffers of the stage."""
    try:
        time.sleep(0.1)
        dev.flushInput()
        dev.flushOutput()
        time.sleep(0.1)
        dev.readline()
    except serial.SerialException:
        time.sleep(0.1)



def get_pos(dev):
    """Get absolute position of stage."""
    x = get_x_pos(dev)
    y = get_y_pos(dev)
    #z = get_z_pos(dev)
    return (x, y)#, z)


def get_status(dev):
    """Get device status."""
    dev.write(('UF\r\r').encode())
    return dev.readline().decode()


def move_by(dev, dx, dy):
    """Move stage by dx and dy units."""
    dx = str(int(dx))
    dy = str(int(dy))
    dev.write(('U\07v\rU\00'+dx+'\rU\01'+dy+'\rUP\r').encode())
    clear_stage_buffer(dev)



def move_to(dev, x, y):
    """Move stage to absolute position."""
    # clear stage buffer
    time.sleep(0.5)
    dev.flushInput()
    dev.flushOutput()    
    # get current stage position
    x_current, y_current = get_pos(dev)
    print(x_current, y_current)
    # determine delta x, y needed to move to new position
    dx, dy = x-x_current, y-y_current
    move_by(dev, dx, dy)


if __name__ == '__main__':
    
    #print_ports()
    
    address = 'COM22'
    dev = serial.Serial(port=address,
                        timeout=2,
                        stopbits=serial.STOPBITS_TWO)
    
    mcl = {
            'dev': dev,
            'set_x': 31,
            'set_y': -22}
    

    for i in range(10):
        
        current_x, current_y = get_x_pos(dev), get_y_pos(dev)
        print('position: {}'.format((current_x, current_y)))
        # move to new position
        dx, dy = 2, 5
        move_by(mcl['dev'], dx, dy)
        print('Device status: {}'.format(get_status(dev)))
    
    dev.close()




