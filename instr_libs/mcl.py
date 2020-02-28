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
    items = ['seq_mcl', 'set_x', 'set_y', 'grid_xf', 'show_x', 'show_y',
             'grid_yf', 'grid_xi', 'grid_yi', 'grid_xsteps',
             'grid_ysteps', 'move_to_zero']
    [mcl[i].setEnabled(enabled) for i in items]
    mcl['address'].setEnabled(not enabled)


def stage_on(mcl):
    "Run this function when MCL-3 stage checkbox is checked."""
    if mcl['on'].isChecked():
        try:
            dev = serial.Serial(
                    port=mcl['address'].text(),
                    timeout=2,
                    stopbits=serial.STOPBITS_TWO)
            mcl['dev'] = dev
            mcl['outbox'].append('Marzhauser MCL-3 stage connected.')
            clear_stage_buffer(dev)
            mcl['outbox'].append('Stage status: {}'.format(get_status(dev)))
            enable_stage(mcl, True)
            x, y = get_x_pos(mcl['dev']), get_y_pos(mcl['dev'])
            mcl['show_x'].setText(str(x))
            mcl['show_y'].setText(str(y))
            mcl['set_x'].setValue(int(x))
            mcl['set_y'].setValue(int(y))
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


def get_grid(mcl):
    """Get grid coordinates from grid settings on GUI."""
    x_cords = np.linspace(mcl['grid_xi'].value(),
                          mcl['grid_xf'].value(),
                          mcl['grid_xsteps'].value()+1)
    y_cords = np.linspace(mcl['grid_yi'].value(),
                          mcl['grid_yf'].value(),
                          mcl['grid_ysteps'].value()+1)
    grid_cords = np.array(np.meshgrid(x_cords, y_cords)).T.reshape(-1,2)
    print(grid_cords)
    return grid_cords


def update_position(mcl):
    """Update position on the main GUI."""
    new_x = int(mcl['set_x'].value())
    new_y = int(mcl['set_y'].value())
    # get current position and update GUI fields
    current_x = get_x_pos(mcl['dev'], backup=int(mcl['show_x'].text()))
    current_y = get_y_pos(mcl['dev'], backup=int(mcl['show_y'].text()))
    #current_x = get_x_pos(mcl['dev'])
    #current_y = get_y_pos(mcl['dev'])    
    
    mcl['show_x'].setText(str(current_x))
    mcl['show_y'].setText(str(current_y))    
    # move to new position 
    dx, dy = new_x-current_x, new_y-current_y
    if dx != 0 or dy != 0:
        mcl['outbox'].append(
                'Moving stage to ({}, {})...'.format(new_x, new_y))
        move_by(mcl['dev'], dx, dy)
        clear_stage_buffer(mcl['dev'])


def get_x_pos(dev, backup=0):
    """Get current X position of stage."""
    try:
        dev.write(('UC\r\r').encode())
        x_pos = dev.readline().decode()
    except AttributeError:
        x_pos = backup
    return int(x_pos)


def get_y_pos(dev, backup=0):
    """Get current Y position of stage."""
    try:
        dev.write(('UD\r\r').encode())
        y_pos = dev.readline().decode()
    except AttributeError:
        y_pos = backup
    return int(y_pos)


def clear_stage_buffer(dev):
    """Clear the input/output buffers of the stage."""
    time.sleep(0.1)
    dev.flushInput()
    dev.flushOutput()
    time.sleep(0.1)
    dev.readline()






'''
def get_x_pos(dev, backup=0):
    """Get current X position of stage."""
    try:
        dev.write(('UC\r\r').encode())
        x_pos = int(dev.readline().decode())
    except:
        x_pos = backup
        time.sleep(0.2)
        print('x failed')
    return x_pos


def get_y_pos(dev, backup=0):
    """Get current Y position of stage."""
    try:
        dev.write(('UD\r\r').encode())
        y_pos = int(dev.readline().decode())
    except:
        y_pos = backup
        time.sleep(0.2)
        print('y failed')
    return y_pos
'''

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




