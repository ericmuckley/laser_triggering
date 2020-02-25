# -*- coding: utf-8 -*-
"""

Module for controlling SRS DG645 digital delay pulse generator.

Created on Mon Feb 17 14:08:13 2020
@author: ericmuckley@gmail.com
"""

import time
import serial
import visa
import thorlabs_apt as apt
from serial.tools import list_ports

def pulsegen_on(srs):
    "Run this function when pulse generator checkbox is checked."""
    if srs['on'].isChecked():
        try:
            dev = serial.Serial(port=srs['address'].text(), timeout=2)
            dev.write('*IDN?\r'.encode())
            srs['dev'] = dev
            srs['outbox'].append('Pulse generator connected.')
            message = dev.readline().decode("utf-8")
            if 'Stanford Research Systems' not in message:
                srs['outbox'].append('Pulse generator could not connect.')
                raise Exception    
            else:
                srs['outbox'].append(message)
                enable_pulse_gen_buttons(srs, True)
        except serial.SerialException:
            srs['outbox'].append('Pulse generator could not connect.')
            srs['on'].setChecked(False)
            enable_pulse_gen_buttons(srs, False)
            srs['dev'] = None
    if not srs['on'].isChecked():
        try:
            srs['dev'].close()
        except AttributeError:
            pass
        srs['dev'] = None
        srs['outbox'].append('Pulse generator closed.')
        srs['on'].setChecked(False)
        enable_pulse_gen_buttons(srs, False)
  
    
def enable_pulse_gen_buttons(srs, enable):
    """Enable/disable buttons related to pulse generator."""
    srs['address'].setEnabled(not enable)
    srs['width'].setEnabled(enable)
    srs['delay'].setEnabled(enable)
    srs['amplitude'].setEnabled(enable)
    srs['number'].setEnabled(enable)
    srs['trigger'].setEnabled(enable)
    srs['seq_laser_trigger'].setEnabled(enable)
    
    
def trigger_pulses(srs):
    """Fire a single burst of n pulses with spacing in seconds."""
    srs['trigger'].setEnabled(False)
    # set pulse width in seconds
    pulse_width = srs['width'].value()/1e3
    pulse_amplitude = srs['amplitude'].value()
    pulse_delay = srs['delay'].value()/1e3
    pulse_number = srs['number'].value()
    srs['outbox'].append('Triggering {} pulses...'.format(pulse_number))
    # set trigger source to single shot trigger
    srs['dev'].write('TSRC5\r'.encode())
    # set delay of A and B outputs
    srs['dev'].write(('DLAY2,0,'+str(0)+'\r').encode())
    srs['dev'].write(('DLAY3,2,'+str(pulse_width)+'\r').encode())
    # set amplitude of output A
    srs['dev'].write(('LAMP1,'+str(pulse_amplitude)+'\r').encode())
    for _ in range(pulse_number):
        # initiate single shot trigger
        srs['dev'].write('*TRG\r'.encode())
        time.sleep(pulse_delay)
    srs['trigger'].setEnabled(True)
    srs['outbox'].append('Pulse sequence complete.')
    srs['tot_pulses'] += pulse_number



if __name__ == '__main__':
    
    rm = visa.ResourceManager()
    
    print('Available ports:')
    print([p for p in rm.list_resources()])
    print([p.device for p in list_ports.comports()])
    print([p for p in apt.list_available_devices()])
    
    
    address = 'COM16'

    dev = serial.Serial(port=address, timeout=2)
    dev.write('*IDN?\r'.encode())

    message = dev.readline().decode("utf-8")
    print(message)
    
    dev.close()

