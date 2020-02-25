# -*- coding: utf-8 -*-
"""

Module to control the Thorlabs KCD101 K-Cube brushed motor controller.
Fuctionality is based on code available here:
https://github.com/qpit/thorlabs_apt/blob/master/thorlabs_apt/core.py

Created on Wed Feb 19 10:07:30 2020
@author: ericmuckley@gmail.com
"""

import thorlabs_apt as apt
import numpy as np

def enable_polarizer(kcube, enable):
    """Enable/disable buttons related to polarizer controller."""
    kcube['phome'].setEnabled(enable)
    kcube['pangle'].setEnabled(enable)
    kcube['curr_pangle_label'].setEnabled(enable)
    kcube['seq_polarizer_rot'].setEnabled(enable)
    kcube['rotation_end'].setEnabled(enable)
    kcube['rotation_start'].setEnabled(enable)
    kcube['rotation_steps'].setEnabled(enable)
    kcube['seq_polarizer_rot'].setEnabled(enable)
    kcube['polarizer_move_to'].setEnabled(enable)
    kcube['paddress'].setEnabled(not enable)
    


def enable_analyzer(kcube, enable):
    """Enable/disable buttons related to analyzer controller."""
    kcube['ahome'].setEnabled(enable)
    kcube['aangle'].setEnabled(enable)
    kcube['curr_aangle_label'].setEnabled(enable)
    kcube['seq_polarizer_rot'].setEnabled(enable)
    kcube['rotation_end'].setEnabled(enable)
    kcube['rotation_start'].setEnabled(enable)
    kcube['rotation_steps'].setEnabled(enable)
    kcube['seq_polarizer_rot'].setEnabled(enable)
    kcube['analyzer_move_to'].setEnabled(enable)
    kcube['aaddress'].setEnabled(not enable)


def polarizer_on(kcube):
    """Polarizer checkbox is checked or unchecked."""
    if kcube['p_on'].isChecked():
        try:
            kcube['pdev'] = apt.Motor(int(kcube['paddress'].text()))
            kcube['outbox'].append('Polarizer controller connected.')
            kcube['outbox'].append(str(kcube['pdev'].hardware_info))
            kcube['outbox'].append(
                    'Serial num: '+str(kcube['pdev'].serial_number))
            enable_polarizer(kcube, True)
            # this allows rotation in both directions
            kcube['pdev'].set_hardware_limit_switches(1,1)
            # set initial angle to be current angle when program started
            kcube['pangle'].setValue(round(kcube['pdev'].position))
        except:
            kcube['outbox'].append('Polarizer controller could not connect.')
            enable_polarizer(kcube, False)
            kcube['p_on'].setChecked(False)
            kcube['pdev'] = None
            kcube['curr_pangle_label'].setText('---   ')
    if not kcube['p_on'].isChecked():
        kcube['pdev'] = None
        enable_polarizer(kcube, False)
        kcube['p_on'].setChecked(False)
        kcube['curr_pangle_label'].setText('---   ')
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
            # this allows rotation in both directions
            kcube['adev'].set_hardware_limit_switches(1,1)
            # set initial angle to be current angle when program started
            kcube['aangle'].setValue(round(kcube['adev'].position))
        except:
            kcube['outbox'].append('Analyzer controller could not connect.')
            enable_analyzer(kcube, False)
            kcube['a_on'].setChecked(False)
            kcube['adev'] = None
            kcube['curr_aangle_label'].setText('---   ')
    if not kcube['a_on'].isChecked():
        kcube['adev'] = None
        enable_analyzer(kcube, False)
        kcube['a_on'].setChecked(False)
        kcube['curr_aangle_label'].setText('---   ')
        kcube['outbox'].append('Analyzer controller closed.')


def get_angle_steps(kcube):
    """Get angle steps from the GUI."""
    return np.linspace(kcube['rotation_start'].value(),
                       kcube['rotation_end'].value(),
                       num=1+kcube['rotation_steps'].value()).astype(int)


def p_in_motion(kcube):
    """Check if polarizer is still moving."""
    return kcube['pdev'].is_in_motion


def a_in_motion(kcube):
    """Check if polarizer is still moving."""
    return kcube['adev'].is_in_motion


def polarizer_move_to(kcube):
    """Move the polarizer to specified angle."""
    angle = int(kcube['pangle'].value())
    kcube['pdev'].move_to(angle)
    kcube['curr_pangle_label'].setText(str(angle))
    #str(round(kcube['pdev'].position)))
            
    
def analyzer_move_to(kcube):
    """Move the analyzer to specified angle."""
    angle = int(kcube['aangle'].value())
    kcube['adev'].move_to(angle)
    kcube['curr_aangle_label'].setText(str(angle))
    #str(round(kcube['adev'].position)))  


def polarizer_home(kcube):
    """Move the polarizer to its home position."""
    kcube['pangle'].setValue(0)
    kcube['pdev'].move_to(0)
    #kcube['curr_pangle_label'].setText(
    #        str(round(kcube['pdev'].position)))  
    #kcube['pdev'].move_home()
    #


def analyzer_home(kcube):
    """Move the analizer to its home position."""
    kcube['aangle'].setValue(0)
    kcube['adev'].move_to(0)
    #kcube['curr_aangle_label'].setText(
    #        str(round(kcube['adev'].position)))  
    #kcube['adev'].move_home()
    #kcube['pangle'].setValue(0)



if __name__ == '__main__':
    
    print(apt.list_available_devices())

    dev = apt.Motor(27255762)
    
    #print(dev.hardware_info)
    #print(dev.is_in_motion)
    #dev.set_velocity_parameters(0, 25, 25)
    # max velocity and aceleration = 25.0
    #dev.set_move_home_parameters(direction, lim_switch, velocity,zero_offset)

    #print(dev.get_move_home_parameters())
    #dev.move_home()
    #dev.move_to(20)
    #dev.move_by(5)
    #dev.move_velocity(0)
    #dev.move_by(5)
    
    #print(dev.is_in_motion)
    dev.move_to(75)
    #dev.set_move_home_parameters(1, 4, 20, 0)
    #dev.set_velocity_parameters(0, 20, 25)
    #dev.set_hardware_limit_switches(1,1)

    print(dev.position)
    print(dev.is_in_motion)
