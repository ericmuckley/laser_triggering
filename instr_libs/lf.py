# -*- coding: utf-8 -*-
"""

Modules for controlling Princeton Instruments software LightField.

Created on Mon Feb 17 17:56:21 2020
@author: ericmuckley@gmail.com
"""

#  LightField dependencies 
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from PyQt5.QtWidgets import QFileDialog


import clr  # the .NET class library
import System.IO as sio  # for saving and opening files
# Import c compatible List and String
from System import String
from System.Collections.Generic import List
# Add needed dll references for LightField
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('System.IO')
clr.AddReference('System.Collections')
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')
# Princeton Instruments imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import DeviceType 

# ------- change matplotlib settings to make plots look nicer --------------

plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['axes.linewidth'] = 3
plt.rcParams['xtick.minor.width'] = 3
plt.rcParams['xtick.major.width'] = 3
plt.rcParams['ytick.minor.width'] = 3
plt.rcParams['ytick.major.width'] = 3
plt.rcParams['figure.autolayout'] = True


def launch_lf(lf):
    """Launch LightField software."""
    lf['outbox'].append('Opening LightField...')
    # kill the process which opens LightField if its already running
    #os.system("taskkill /f /im AddInProcess.exe")
    # create a C# compatible List of type String object
    lf_exp_list = List[String]()
    # add the command line option for an empty experiment
    lf_exp_list.Add("/empty")#("Default_Python_Experiment")#
    # create the LightField Application (true for visible)
    # the 2nd parameter is the experiment name to load 
    lf['app'] = Automation(True, List[String](lf_exp_list))
    lf['acquire'].setEnabled(True)
    lf['notes'].setEnabled(True)
    lf['seq'].setEnabled(True)
    lf['outbox'].append('LightField opened.')
    lf['outbox'].append('Now load "Default_Python_Experiment" in Lightfield.')


def device_found(experiment):
    "Check if devices are connected to LightField."""
    for device in experiment.ExperimentDevices:
        if (device.Type == DeviceType.Camera):
            return True


def save_file(filename, experiment):    
    """Save a Raman acquisition file using LightField."""
    # Set the base file name
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationBaseFileName,
        sio.Path.GetFileName(filename))
    # Option to Increment, set to false will not increment
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationAttachIncrement, False)
    # Option to add date
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationAttachDate, False)
    # Option to add time
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationAttachTime, False)


def show_file_list(lf):
    """Show the list of acquired Raman spe files."""
    lf['outbox'].append(
            '{} Raman acquisition files'.format(len(lf['file_list'])))
    for f in lf['file_list']:
        lf['outbox'].append(f)


def acquire_raman(lf):
    """Acquire Raman spectra using an opened instance of LightField."""
    # get current loaded experiment
    experiment = lf['app'].LightFieldApplication.Experiment
    # check for device and inform user if one is needed
    if (device_found(experiment)==True):        
        file_name = time.strftime('%Y-%m-%d_%H-%M-%S')
        lf['recent_file'] = file_name
        lf['file_list'].append(file_name+'.csv')
        # pass location of saved file
        save_file(file_name, experiment)
        time.sleep(0.2)
        # acquire image
        experiment.Acquire()
        time.sleep(0.2)
        lf['outbox'].append('Raman data saved to:')
        lf['outbox'].append(
                str(experiment.GetValue(
                        ExperimentSettings.FileNameGenerationDirectory)))
    else:
        lf['outbox'].append('No LightField-compatible devices found.')
        lf['outbox'].append(
                'Please load "Default_Python_Experiment" in Lightfield.')



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


def stack_spectra(filelist):
    """Get a 2D array of stacked spectra and metadata in a dictionary."""
    d = {
        'colors': cm.jet(np.linspace(0, 1, len(filelist))),
        'labels': []}
    # loop over each spectrum and stack it into 2D array
    for fi, f in enumerate(filelist):
        df = pd.read_csv(f)
        d['labels'].append(os.path.split(f)[1].split('.csv')[0])
        # stack spectra together in a single matrix
        if fi == 0:
            d['spec_mat'] = np.array(df['Intensity'])
        else:
            d['spec_mat'] = np.column_stack((d['spec_mat'], df['Intensity']))
        d['wavelength'] = np.array(df['Wavelength'])
    return d


def plot_raman_files_from_selection(lf):
    """Plot Raman data from files selected using a user dialog."""
    qfd = QFileDialog()
    qfd.setFileMode(QFileDialog.ExistingFiles)
    filenames = qfd.getOpenFileNames(
        qfd,
        caption='Select Raman CSV files',
        filter='CSV (*.csv)',
        directory=lf['raman_dir'])[0]
    
    # get array of spectral information
    d = stack_spectra(filenames)

    # plot Raman spectra as lines
    if len(list(d['labels'])) == 0:
        lf['outbox'].append('No spectra selected.')
    if len(list(d['labels'])) == 1:
        plt.ion()
        fig = plt.figure(1)
        fig.clf()
        plt.plot(d['wavelength'], d['spec_mat'], lw=1)
        plot_setup(
            labels=('Wavelength (nm)', 'Intensity (counts)'),
            legend=False)
        fig.canvas.set_window_title('Raman spectra')
        plt.draw()
    if len(list(d['labels'])) > 1:
        plt.ion()
        fig = plt.figure(1)
        fig.clf()
        for i in range(np.shape(d['spec_mat'])[1]):
            plt.plot(
                d['wavelength'], d['spec_mat'][:, i],
                label=d['labels'][i], c=d['colors'][i], lw=1)

        plot_setup(labels=('Wavelength (nm)', 'Intensity (counts)'),
                       legend=True)
        fig.canvas.set_window_title('Raman spectra')
        plt.draw()

        # plot Raman spectra as heatmap
        plt.ion()
        fig = plt.figure(2)
        fig.clf()
        plot_extent = [0, len(d['labels']),
            np.min(d['wavelength']),
            np.max(d['wavelength'])]
        plt.imshow(
            d['spec_mat'],
            aspect='auto',
            origin='lower',
            cmap='jet',    extent=plot_extent,
            vmin=np.min(d['spec_mat']),
            vmax=np.max(d['spec_mat']))
        plot_setup(
            colorbar=True, legend=False,
            title='Raman counts over time',
            labels=('Spectrum number', 'Wavelength (nm)'))
        fig.canvas.set_window_title('Raman spectra over time')
        plt.draw()

    
'''
def plot_grid_intensity(lf):
    """Plot max raman intensity across the sampled grid."""
    # get report which matches raman spectra with log file
    d = create_raman_report(lf['logdir'], raman_dir=lf['raman_dir'])


    # plot max intensity across grid
    plt.ion()
    fig = plt.figure(3)
    fig.clf()
    plt.scatter(d['log']['x_position'],
                d['log']['y_position'],
                s=d['log']['max_intensity']/50)
    plot_setup(colorbar=False, legend=False,
               title='Max. Raman intensity accross grid',
            labels=('X position (cm)', 'Y position (cm)'))
    fig.canvas.set_window_title('Max. Raman intensity across grid')
    plt.draw()
'''






