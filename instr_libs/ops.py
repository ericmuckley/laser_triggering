# -*- coding: utf-8 -*-
"""

This module contains functions which control utilities and operations of
the main GUI.

Created on Mon Feb 17 16:44:03 2020
@author: ericmuckley@gmail.com
"""

import json
import os
import numpy as np
import time
import visa
import pandas as pd
import inspect
import thorlabs_apt as apt
from serial.tools import list_ports
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QSlider, QFileDialog
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton
from PyQt5.QtCore import QSettings
import markdown
import webbrowser
import matplotlib.pyplot as plt
from matplotlib import cm


plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['axes.linewidth'] = 3
plt.rcParams['xtick.minor.width'] = 3
plt.rcParams['xtick.major.width'] = 3
plt.rcParams['ytick.minor.width'] = 3
plt.rcParams['ytick.major.width'] = 3
plt.rcParams['figure.autolayout'] = True


def plot_setup(labels=['X', 'Y'], fsize=14, setlimits=False,
               title=None, legend=True, limits=(0,1,0,1), colorbar=False):
    """Creates a custom plot configuration to make graphs look nice.
    This can be called with matplotlib for setting axes labels,
    titles, axes ranges, and the font size of plot labels.
    This should be called between plt.plot() and plt.show() commands."""
    plt.xlabel(str(labels[0]), fontsize=fsize)
    plt.ylabel(str(labels[1]), fontsize=fsize)
    #fig = plt.gcf()
    #fig.set_size_inches(6, 4)
    if title:
        plt.title(title, fontsize=fsize)
    if legend:
        plt.legend(fontsize=fsize-4)
    if setlimits:
        plt.xlim((limits[0], limits[1]))
        plt.ylim((limits[2], limits[3]))
    if colorbar:
        plt.colorbar()



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



def generate_report(ops, logpath=None):
    """Generate a report which links each Raman spectra with its metadata
    which is stored in the log file."""
    # prompt user to ask for log file 
    if logpath is None:
        logpath = QFileDialog.getOpenFileName(
                    caption='Select log file', filter='CSV (*.csv)',
                    directory=ops['logdir'])[0]
    try:
        log = pd.read_csv(logpath)
    except FileNotFoundError:
        ops['outbox'].append('No log file selected.')
        log = None
    if log is not None:
        ops['selected_logname'] = os.path.split(logpath)[1].split('.')[0]
        # create dictionary to hold all results, metadata, and statistics
        d = {'df': {}, 'log': log}
        max_int_list = []
        max_int_wl_list = []
        
        # loop over each raman file and save to dictionary
        for ri, r in enumerate(log['recent_raman_file']):
            # read raman data file
            df = pd.read_csv(os.path.join(ops['raman_dir'], r+'.csv'),
                             usecols=['Wavelength', 'Intensity'])
            # rename columns and add dataframe to dictionary
            df.columns = ['wl', 'int']
            d['df'][r] = df 
            # calculate some statistics and add to dictionary
            max_int_list.append(float(df['int'].max()))
            max_int_wl_list.append(float(df['wl'].iloc[df['int'].idxmax()]))
        d['log']['max_intensity'] = max_int_list
        d['log']['max_intensity_wavelength'] = max_int_wl_list
        
        ops['report'] = d
        plot_spec_in_report(ops)
        serialize(ops)
    
    
def plot_spec_in_report(ops):
    """Plot the spectra in a log report."""
    # plot Raman spectra as lines
    d = ops['report']
    if len(d['log']) == 0:
        ops['outbox'].append('No spectra selected.')
    else:
        plt.ion()
        fig = plt.figure(5)
        fig.clf()
        colors = cm.jet(np.linspace(0, 1, len(d['log'])))
        for ri, r in enumerate(d['df']):
            plot_setup(
                    colorbar=False, legend=False,
                    title='Raman spectra',
                    labels=('Wavelength (nm)', 'Intensity (counts)'))
            plt.plot(d['df'][r]['wl'], d['df'][r]['int'],
                     #label=r,
                     c=colors[ri], lw=1)
    
    
'''   
    plt.scatter(d['log']['x_position'],
                d['log']['y_position'],
                s=d['log']['max_intensity']/50)
    plot_setup(colorbar=False, legend=False,
               title='Max. Raman intensity accross grid',
            labels=('X position (cm)', 'Y position (cm)'))
    fig.canvas.set_window_title('Max. Raman intensity across grid')
    plt.draw()
'''   
    

def serialize(ops):
    """Serialize a dictionary containing pandas dataframes."""
    filename = os.path.join(
            ops['logdir'], ops['selected_logname']+'_report.json')
    with open(filename, 'w') as fp:
        json.dump(ops['report'], fp, cls=JSONEncoder)



class JSONEncoder(json.JSONEncoder):
    """Class for serializing pandas dataframes using JSON."""
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json(orient='records')
        return json.JSONEncoder.default(self, obj)



    
    


def get_log_row_data(srs, lf, kcube, mcl):
    """Get data for the most recent row of the log file."""
    d = {'time': time.strftime('%Y-%m-%d_%H-%M-%S'),
         'total_pulses': srs['tot_pulses'],
         'pulsewidth_ms':  srs['width'].value()/1e3,
         'pulse_amplitude_V': srs['amplitude'].value(),
         'pulse_delay_ms': srs['delay'].value()/1e3,
         'pulse_number': srs['number'].value(),
         'x_position': mcl['show_x'].text(),
         'y_position': mcl['show_y'].text(),
         'polarizer_angle_deg': kcube['p_set'].value(),
         'notes': lf['notes'].text().replace(',','__').replace('\t', '__'),
         'recent_raman_file': lf['recent_file']}
    return d


def log_to_file(ops, srs, lf, kcube, mcl):
    """Create log file."""
    # get most recent row of data
    d = get_log_row_data(srs, lf, kcube, mcl)
    # assign most recent row to last row in log data
    ops['data'][ops['row_counter']] = list(d.values())
    # convert log data to Pandas DataFrame
    df = pd.DataFrame(columns=list(d.keys()), data=ops['data'])
    # remove empty rows before saving
    df.replace('', np.nan, inplace=True)
    df.dropna(how='all', inplace=True)
    # save dataframe as csv file
    df.to_csv(ops['logpath'], index=False)
    ops['outbox'].append('Log file appended to {}'.format(ops['logpath']))
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
                    ops['logdir'],
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


def load_json(filename):
    """Load the json file report."""
    with open(filename) as fp:
        data = json.load(fp)
    return data

def load_report_from_json(filename):
    """Load a Raman report in JSON format and convert to dataframes."""
    # load json file
    with open(filename) as fp:
        report = json.load(fp)
    # convert serialized data back to dataframes
    if 'df' in report:
        for r in report['df']:
            report['df'][r] = pd.read_json(report['df'][r])
    if 'log' in report:
        report['log'] = pd.read_json(report['log'])
    return report
    



if __name__ == '__main__':
    filename = 'C:\\Users\\Administrator\\Desktop\\eric\\laser_triggering\\logs\\2020-03-10_16-37-27_report.json'
    rep = load_report_from_json(filename)












