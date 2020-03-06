# -*- coding: utf-8 -*-
"""

MOdule for controlling the Marzhauser MCL-3 stage controller.
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


# default scale for the stage is
# 4000 units == 1 cm

# change this variable to reverse the y-direction of the stage movement.
# this is needed if the stage is mounted vertically upside down for example.
# for normal operation, y_dir = 1
#for reverse operation, y_dir = -1
'''
y_dir = 1
if y_dir not in (1, -1):
    y_dir = 1
'''

def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]


def enable_stage(mcl, enabled):
    """Enable/disable GUI objects related to the MCL stage."""
    items = ['seq_mcl', 'set_x', 'set_y', 'grid_xf', 'show_x', 'show_y',
             'grid_yf', 'grid_xi', 'grid_yi', 'grid_xsteps', 'grid_ysteps',
             'preview_grid_cords']
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
            mcl['show_x'].setText(str(round(x, 2)))
            mcl['show_y'].setText(str(round(y, 2)))
            mcl['set_x'].setValue(float(x))
            mcl['set_y'].setValue(float(y))
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

def preview_grid_cords(mcl):
    """Preview the grid coordinates."""
    grid = get_grid(mcl)
    mcl['outbox'].append('Grid coordinates (X, Y):')
    [mcl['outbox'].append(str(g)) for g in grid]


def get_grid(mcl):
    """Get grid coordinates from grid settings on GUI."""
    x_cords = np.linspace(mcl['grid_xi'].value(),
                          mcl['grid_xf'].value(),
                          mcl['grid_xsteps'].value()+1)
    y_cords = np.linspace(mcl['grid_yi'].value(),
                          mcl['grid_yf'].value(),
                          mcl['grid_ysteps'].value()+1)
    grid_cords = np.array(np.meshgrid(x_cords, y_cords)).T.reshape(-1,2)
    return grid_cords


def update_position(mcl):
    """Update position on the main GUI."""
    # get current stage position and update GUI fields
    current_x = get_x_pos(mcl['dev'], backup=float(mcl['show_x'].text()))
    current_y = get_y_pos(mcl['dev'], backup=float(mcl['show_y'].text()))
    mcl['show_x'].setText(str(current_x))
    mcl['show_y'].setText(str(current_y))
    
    # if stage has not moved
    if mcl['prev_position'] == (current_x, current_y):
        mcl['moving'] = False
    # if stage has moved
    else:
        mcl['outbox'].append(
                'Stage moved to ({}, {})'.format(current_x, current_y))

    # reset the previous position
    mcl['prev_position'] = (current_x, current_y)
        
    # get user-defined coordinates from the GUI in centimeters
    new_x = round(mcl['set_x'].value(), 2)
    new_y = round(mcl['set_y'].value(), 2)
    # move to new position 
    dx, dy = round(new_x-current_x, 2), round(new_y-current_y, 2)
    if dx != 0 or dy != 0:
        mcl['moving'] = True
        #mcl['just_moved'] = True
        mcl['outbox'].append(
                'Moving stage to ({}, {})...'.format(new_x, new_y))
        move_by(mcl['dev'], int(dx*4000), int(dy*4000))
        clear_stage_buffer(mcl['dev'])



def get_x_pos(dev, backup=0):
    """Get current X position of stage."""
    clear_stage_buffer(dev)
    try:
        dev.write(('UC\r\r').encode())
        x_pos = dev.readline().decode()
        return round(float(x_pos)/4000, 2)
    except ValueError:
        x_pos = backup
        return round(x_pos, 2)
    


def get_y_pos(dev, backup=0):
    """Get current Y position of stage."""
    clear_stage_buffer(dev)
    try:
        dev.write(('UD\r\r').encode())
        y_pos = dev.readline().decode()
        return round(float(y_pos)/4000, 2)
    except ValueError:
        y_pos = backup
        return round(y_pos, 2)
    


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



def get_z_pos(dev):
    """Get current Z position of stage."""
    dev.readline()  # clears buffer
    dev.write(('UE\r\r').encode())
    return int(dev.readline().decode())


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




