# -*- coding: utf-8 -*-
"""

Module to control the Thorlabs KCD101 K-Cube brushed motor controller.
Fuctionality is based on code available here:
https://github.com/qpit/thorlabs_apt/blob/master/thorlabs_apt/core.py

Created on Wed Feb 19 10:07:30 2020
@author: ericmuckley@gmail.com
"""

import thorlabs_apt as apt


def enable_polarizer(kcube, enable):
    """Enable/disable buttons related to polarizer controller."""
    kcube['pset'].setEnabled(enable)
    kcube['phome'].setEnabled(enable)
    kcube['pangle'].setEnabled(enable)
    kcube['get_p_angle'].setEnabled(enable)
    kcube['paddress'].setEnabled(not enable)


def enable_analyzer(kcube, enable):
    """Enable/disable buttons related to analyzer controller."""
    kcube['aset'].setEnabled(enable)
    kcube['ahome'].setEnabled(enable)
    kcube['aangle'].setEnabled(enable)
    kcube['get_a_angle'].setEnabled(enable)
    kcube['aaddress'].setEnabled(not enable)


def polarizer_on(kcube):
    """Polarizer checkbox is checked or unchecked."""
    if kcube['p_on'].isChecked():
        #try:
        kcube['pdev'] = apt.Motor(int(kcube['paddress'].text()))
        kcube['outbox'].append('Polarizer controller connected.')
        kcube['outbox'].append(str(kcube['pdev'].hardware_info))
        kcube['outbox'].append(
                'Serial num: '+str(kcube['pdev'].serial_number))
        enable_polarizer(kcube, True)
        '''
        except:
            kcube['outbox'].append('Polarizer controller could not connect.')
            enable_polarizer(kcube, False)
            kcube['p_on'].setChecked(False)
            kcube['pdev'] = None
        '''
    if not kcube['p_on'].isChecked():
        kcube['pdev'] = None
        enable_polarizer(kcube, False)
        kcube['p_on'].setChecked(False)
        kcube['outbox'].append('Polarizer controller closed.')


def analyzer_on(kcube):
    """Analyzer checkbox is checked or unchecked."""
    if kcube['a_on'].isChecked():
        try:
            kcube['adev'] = apt.Motor(int(kcube['aaddress'].text()))
            kcube['outbox'].append('Analyzer controller connected.')
            kcube['outbox'].append(str(kcube['adev'].hardware_info))
            kcube['outbox'].append(
                'Serial num: '+str(kcube['adev'].serial_number))
            enable_analyzer(kcube, True)
        except:
            kcube['outbox'].append('Analyzer controller could not connect.')
            enable_analyzer(kcube, False)
            kcube['a_on'].setChecked(False)
            kcube['adev'] = None
    if not kcube['a_on'].isChecked():
        kcube['adev'] = None
        enable_analyzer(kcube, False)
        kcube['a_on'].setChecked(False)
        kcube['outbox'].append('Analyzer controller closed.')


def polarizer_move_to(kcube):
    """Move the polarizer to specified angle."""
    angle = int(kcube['pangle'].value())
    kcube['outbox'].append(
            'Rotating polarizer to {} degrees...'.format(angle))
    kcube['pdev'].move_to(int(kcube['pangle'].value()))
    kcube['outbox'].append('Polarizer rotation complete.')
    

def analyzer_move_to(kcube):
    """Move the analyzer to specified angle."""
    angle = int(kcube['aangle'].value())
    kcube['outbox'].append(
            'Rotating analyzer to {} degrees...'.format(angle))
    kcube['adev'].move_to(int(kcube['aangle'].value()))
    kcube['outbox'].append('Analyzer rotation complete.')


def get_p_angle(kcube):
    """Get the current angle of the polarizer."""
    kcube['outbox'].append(
            'Polarizer angle (deg): '+str(round(kcube['pdev'].position, 2)))


def get_a_angle(kcube):
    """Get the current angle of the analyzer."""
    kcube['outbox'].append(
            'Analyzer angle (deg): '+str(round(kcube['adev'].position, 2)))





if __name__ == '__main__':
    
    print(apt.list_available_devices())

    dev = apt.Motor(27255762)

    #print(dev.hardware_info)
    #print(dev.is_in_motion)
    #dev.set_velocity_parameters(0, 25, 25)
    # max velocity and aceleration = 25.0
    #motor.move_home(True)
    dev.move_to(90)
    #dev.move_by(15)
    print(dev.position)
