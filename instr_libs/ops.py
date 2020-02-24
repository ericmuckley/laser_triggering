# -*- coding: utf-8 -*-
"""

This module contains functions which control utilities and operations of
the main GUI.

Created on Mon Feb 17 16:44:03 2020
@author: ericmuckley@gmail.com
"""

import os
import numpy as np
import time
import visa
import pandas as pd
import inspect
import thorlabs_apt as apt
from serial.tools import list_ports
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QSlider
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton
from PyQt5.QtCore import QSettings
import markdown
import webbrowser



def show_help():
    """Show help popup window. First, generate the HTML using the markdown
    README.md file. Then show the HTML page in the default browser."""
    # get parent directory
    #parent_folder = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    # generate html page from markdown README.md file
    md_filename = os.path.join(os.getcwd(), 'README.md')
    #md_filename = os.path.join(parent_folder, 'README.md')
    html_filename = os.path.join(os.getcwd(), 'README.html')
    markdown.markdownFromFile(input=md_filename, output=html_filename)                            
    # open help in web browser
    webbrowser.open(html_filename)





def show_log_path(ops):
    """Show the path to the log file."""
    ops['outbox'].append('Log file path: %s' %(ops['logpath']))


def get_log_row_data(srs, lf, kcube):
    """Get data for the most recent row of the log file."""
    d = {'time': time.strftime('%Y-%m-%d_%H-%M-%S'),
         'total_pulses': srs['tot_pulses'],
         'pulsewidth_ms':  srs['width'].value()/1e3,
         'pulse_amplitude_V': srs['amplitude'].value(),
         'pulse_delay_ms': srs['delay'].value()/1e3,
         'pulse_number': srs['number'].value(),
         'polarizer_angle_deg': kcube['pangle'].value(),
         'recent_raman_file': lf['recent_file']}
    return d


def log_to_file(ops, srs, lf, kcube):
    """Create log file."""
    # get most recent row of data
    d = get_log_row_data(srs, lf, kcube)
    # assign most recent row to last row in log data
    ops['data'][ops['row_counter']] = list(d.values())
    # convert log dtaa to Pandas DataFrame
    df = pd.DataFrame(columns=list(d.keys()),
                          data=ops['data'])
    # remove empty rows before saving
    df.replace('', np.nan, inplace=True)
    df.dropna(how='all', inplace=True)
    # save dataframe as csv file
    df.to_csv(ops['logpath'], index=False)
    ops['outbox'].append('Log file appended.')
    ops['row_counter'] += 1



def print_ports(ops):
    """Print a list of available serial and VISA ports."""
    rm = visa.ResourceManager()
    visa_ports = list(rm.list_resources())
    ser_ports = list(list_ports.comports())
    ftid_usb_ports = list(apt.list_available_devices())
    ops['outbox'].append('Available instrument addresses:')
    [ops['outbox'].append('Visa port: '+str(p)) for p in visa_ports]
    [ops['outbox'].append('Serial port: '+str(p.device)) for p in ser_ports]
    [ops['outbox'].append('FTID USB port: '+str(p)) for p in ftid_usb_ports]
    


def export_settings(ops):
    # export app settings from file
    ops['outbox'].append('Exporting experiment settings...')
    # create filepath for saved settings
    settings_filepath = os.path.join(
                    ops['filedir'],
                    ops['starttime']+'_experiment_settings.ini')
    # save the name of the settigns filepath
    ops['app_settings_filename'] = settings_filepath
    # create settings .ini file
    settings = QSettings(settings_filepath, QSettings.IniFormat)

    # scroll through each GUI widget and write its data to settings file
    for name, obj in inspect.getmembers(ops['app']):
        if isinstance(obj, QComboBox):
            name = obj.objectName()
            text = obj.itemText(obj.currentIndex())
            settings.setValue(name, text)
        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)
        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            state = obj.checkState()
            settings.setValue(name, state)
        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = obj.isChecked()
            settings.setValue(name, value)
        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = obj.value()
            settings.setValue(name, value)
        if isinstance(obj, QDoubleSpinBox):
            name = obj.objectName()
            value = obj.value()
            settings.setValue(name, value)
        if isinstance(obj, QSlider):
            name = obj.objectName()
            value = obj.value()
            settings.setValue(name, value)

    ops['app_settings'] = settings
    ops['outbox'].append('Experiment settings exported.')


def str_to_bool(inp_str):
    # converts string to boolean value
    out = False
    if inp_str == 1:
        out = True
    elif inp_str == 0:
        out = False
    elif inp_str == '1':
        out = True
    elif inp_str == '2':
        out = True
    elif inp_str == 2:
        out = True
    elif inp_str == '0':
        out = False
    elif inp_str == 'True':
        out = True
    elif inp_str == 'False':
        out = False
    elif inp_str is None:
        pass
    else:
        pass
    return out


def import_settings(ops, filepath):
    # import app settings from file and restore them in widgets
    ops['outbox'].append('Importing experiment settings...')
    settings = QSettings(filepath, QSettings.IniFormat)

    # loop over each widget on GUI and resotre its values from settings file
    for name, obj in inspect.getmembers(ops['app']):
        if isinstance(obj, QComboBox):
            index = obj.currentIndex()
            # text   = obj.itemText(index)
            name = obj.objectName()
            value = (settings.value(name))
            # if value == '':
            #    continue
            index = obj.findText(value)
            if index == -1:  # add to list if not found
                obj.insertItems(0, [value])
                index = obj.findText(value)
                obj.setCurrentIndex(index)
            else:
                obj.setCurrentIndex(index)
        elif isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = settings.value(name)  # .decode('utf-8'))
            if value is not None:
                obj.setText(str(value))
        elif isinstance(obj, QCheckBox):
            name = obj.objectName()
            value = settings.value(name)
            if value is not None:
                obj.setChecked(str_to_bool(value))
        elif isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = settings.value(name)
            if value is not None:
                obj.setChecked(str_to_bool(value))
        elif isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            if value is not None:
                obj.setValue(int(value))
        elif isinstance(obj, QDoubleSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            if value is not None:
                obj.setValue(float(value))
        elif isinstance(obj, QLabel):
            pass
        else:
            pass
    ops['outbox'].append(
            'Experiment settings imported from '+filepath)





'''

def set_directory(self):
    """Set the directory for saving files."""
    self.filedir = str(QFileDialog.getExistingDirectory(
            self, 'Select a directory for storing data'))
    self.ui.outbox.append('File directory is set to ' + self.filedir)


def show_directory(self):
    """Show the file directory in the output box."""
    self.ui.outbox.append('File directory is set to ' + self.filedir)



def plot_df_surf(self):
    """Plot delta F surface."""
    plt.cla()
    fig_df = plt.figure(5)
    plt.ion()
    plt.contour(self.contours['mu_mesh'], self.contours['eta_mesh'],
                self.contours['df_surf'], self.contours['df_exp'])
    plt.contourf(self.contours['mu_mesh'], self.contours['eta_mesh'],
                 self.contours['df_surf'], 50, cmap='rainbow')
    self.plot_setup(title='Δf (Hz/cm^2)',
               labels=['Log (μ) (Pa)', 'Log (η) (Pa s)'], colorbar=True)
    plt.tight_layout()
    fig_df.canvas.set_window_title('Δf surface')
    fig_df.show()

'''
