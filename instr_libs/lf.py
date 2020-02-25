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




def launch_lf(lf):
    """Launch LightField software."""
    # kill the process which opens LightField if its already running
    os.system("taskkill /f /im AddInProcess.exe")
    # create a C# compatible List of type String object
    lf_exp_list = List[String]()
    # add the command line option for an empty experiment
    lf_exp_list.Add("Default_Python_Experiment")#("/empty")
    # create the LightField Application (true for visible)
    # the 2nd parameter is the experiment name to load 
    lf['app'] = Automation(True, List[String](lf_exp_list))
    lf['acquire'].setEnabled(True)
    lf['notes'].setEnabled(True)
    lf['seq'].setEnabled(True)


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
        # check this location for saved spe after running
        #notes = lf['notes'].text().replace(',','__').replace('\t', '__')
        file_name = time.strftime('%Y-%m-%d_%H-%M-%S')#+'___'+notes
        lf['recent_file'] = file_name
        lf['file_list'].append(file_name+'.csv')
        # pass location of saved file
        save_file(file_name, experiment)
        # acquire image
        experiment.Acquire()
        lf['outbox'].append(str(String.Format("{0} {1}", "Data saved to",
          experiment.GetValue(ExperimentSettings.
                              FileNameGenerationDirectory))))
    else:
        lf['outbox'].append('No LightField-compatible devices found.')


def plot_file_list(lf):
    """Plot the Raman acquisition spectra. They should be in csv
    format as specified by the Default_Python_Experiment file
    in LightField."""
    if len(lf['file_list']) > 0:
        p='C:\\Users\\Administrator\\Documents\\LightField\\csv_files\\'
        colors = cm.jet(np.linspace(0, 1, len(lf['file_list'])))
        plt.ion()
        fig = plt.figure(0)
        fig.clf()
        for fi, f in enumerate(lf['file_list']):
            df = pd.read_csv(p+str(f))
            plt.plot(df['Wavelength'], df['Intensity'], label=fi,
                     c=colors[fi], lw=1)
        plot_setup(labels=('Wavelength (nm)', 'Intensity (counts)'))
        fig.canvas.set_window_title('Spectra')
        plt.draw()



def plot_setup(labels=['X', 'Y'], fsize=20, setlimits=False,
               title=None, legend=True, limits=(0,1,0,1)):
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

    
