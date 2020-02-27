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


def get_x_pos(dev):
    """Get current X position of stage."""
    dev.write(('UC\r\r').encode())
    return int(dev.readline().decode())


def get_y_pos(dev):
    """Get current Y position of stage."""
    dev.write(('UD\r\r').encode())
    return int(dev.readline().decode())


def get_z_pos(dev):
    """Get current Z position of stage."""
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
    # clear stage buffer
    time.sleep(0.5)
    dev.flushInput()
    dev.flushOutput()


def move_to(dev, x, y):
    """Move stage to absolute position."""
    # clear stage buffer
    time.sleep(0.5)
    dev.flushInput()
    dev.flushOutput()    
    # get current stage position
    x_current, y_current = get_pos(dev)
    # determine delta x, y needed to move to new position
    dx, dy = x-x_current, y-y_current
    move_by(dev, dx, dy)


   'dev': None,
   'on': self.ui.mcl_on,
   'seq_mcl': self.ui.seq_mcl,
   'set_x': self.ui.mcl_set_x,
   'set_y': self.ui.mcl_set_y,
   'address': self.ui.mcl_address,
   'grid_xf': self.ui.mcl_grid_x_end,
   'grid_yf': self.ui.mcl_grid_y_end,
   'grid_xi': self.ui.mcl_grid_x_start,
   'grid_yi': self.ui.mcl_grid_y_start,
   'grid_xsteps': self.ui.mcl_grid_x_steps,
   'grid_ysteps': self.ui.mcl_grid_y_steps,
   'move_to_zero': self.ui.mcl_move_to_zero}



def enable_stage(mcl, enabled):
    """Enable/disable GUI objects related to the MCL stage."""
    items = ['seq_mcl', 'set_x', 'set_y', 'grid_xf',
             'grid_yf', 'grid_xi', 'grid_yi', 'grid_xsteps',
             'grid_ysteps', 'move_to_zero']
    [mcl[i].setEnabled(enabled) for i in items]
    mcl['address'].setEnabled(not enabled)


def stage_on(mcl):
    "Run this function when MCL-3 stage checkbox is checked."""
    if mcl['on'].isChecked():
        try:
            dev = serial.Serial(port=mcl['address'].text()),
                        timeout=2, stopbits=serial.STOPBITS_TWO)
            mcl['dev'] = dev
            mcl['outbox'].append('Marzhauser MCL-3 stage connected.')
            mcl['outbox'].append(
                    'Device status: {}'.format(get_status(dev)))
            enable_stage(mcl, True)
        except:
            mcl['outbox'].append('Stage could not connect.')
            enabe_stage(mcl, False)
            mcl['dev'] = None
            mcl['on'].setChecked(False)
    if not mcl['on'].isChecked():
        try:
            mcl['dev'].close()
        except AttributeError:
            pass
        mcl['dev'] = None
        mcl['outbox'].append('Stage closed.')
        enable_stage(mcl, False)
        mcl['on'].setChecked(False)


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

    


if __name__ == '__main__':
    
    #print_ports()
    
    address = 'COM22'
    dev = serial.Serial(port=address,
                        timeout=2,
                        stopbits=serial.STOPBITS_TWO)
    
    
    print('Device status: {}'.format(get_status(dev)))

    move_to(dev, 2, 4)
    
    print('position: {}'.format(get_pos(dev)))
    print('Device status: {}'.format(get_status(dev)))
    
    
    dev.close()




