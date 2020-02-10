# -*- coding: utf-8 -*-

"""
GUI applicaton for measuring Raman using Princeton Instruments
LightField software and controlling laser pulses using an
SRS DG645 digital delay pulse generator.

To see help, run this file to open the GUI,
then navigate to Menu --> Show Help.

Updated version is stored at
https://github.com/ericmuckley/laser_triggering



Created on Feb 3 2020
@author: ericmuckley@gmail.com

"""

# --------------------- core GUI libraries --------------------------------
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog
#from PyQtCore import QRunnable, QThreadPool, pyqtSlot
import os
import sys
import time
import serial
from serial.tools import list_ports
#import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt




# --------------------- for LightField dependencies ------------------------
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


'''
# change matplotlib settings to make plots look nicer
plt.rcParams['xtick.labelsize'] = 20
plt.rcParams['ytick.labelsize'] = 20
plt.rcParams['axes.linewidth'] = 3
plt.rcParams['xtick.minor.width'] = 3
plt.rcParams['xtick.major.width'] = 3
plt.rcParams['ytick.minor.width'] = 3
plt.rcParams['ytick.major.width'] = 3
plt.rcParams['figure.autolayout'] = True
'''

class Worker(QtCore.QRunnable):
    """Class to start a new worker thread for background tasks.
    Call this thread inside a main GUI function by:
    worker = Worker(self.function_to_execute) #, pass other args here,...,)
    self.threadpool.start(worker)."""
    def __init__(self, fn, *args, **kwargs):
        """This allows the Worker class to take any function as an
        argument, along with args, and run it in a separate thread."""
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    @QtCore.pyqtSlot()
    def run(self):
        """Take a function and its args which were passed to the Worker
        class and execute it in a new thread."""
        self.fn(*self.args, **self.kwargs)
  


class App(QMainWindow):
    """Class which creates the main window of the application."""

    # load Qt designer XML .ui GUI file
    Ui_MainWindow, QtBaseClass = uic.loadUiType('ui.ui')

    def __init__(self):

        super(App, self).__init__()
        self.ui = App.Ui_MainWindow()
        self.ui.setupUi(self)

        # initialize multithreading
        self.threadpool = QtCore.QThreadPool()

        # assign functions to top menu items
        # example: self.ui.menu_item_name.triggered.connect(self.function_name)
        #self.ui.actionShowfiledir.triggered.connect(self.show_directory)
        #self.ui.actionChangefiledir.triggered.connect(self.set_directory)
        self.ui.quitapp.triggered.connect(self.quitapp)
        self.ui.print_ports.triggered.connect(self.print_ports)
        self.ui.show_help.triggered.connect(self.show_help)

        # assign actions to GUI buttons
        # example: self.ui.BUTTON_NAME.clicked.connect(self.FUNCTION_NAME)
        self.ui.trigger_pulses.clicked.connect(self.trigger_pulses_thread)
        self.ui.acquire_raman.clicked.connect(self.acquire_raman)
        self.ui.run_seq.clicked.connect(self.run_seq_thread)
        self.ui.abort_seq.clicked.connect(self.abort_seq)
        self.ui.launch_lf.clicked.connect(self.launch_lf)
        
        # assign actions to checkboxes
        # example: self.ui.CHECKBOX.stateChanged.connect(self.FUNCTION_NAME)
        self.ui.pulsegen_on.stateChanged.connect(self.pulsegen_on)
        
        # set default data folder and create it if it doesn't exist
        #self.filedir = os.getcwd()+'\\QCMD_model_results'
        #if not os.path.exists(self.filedir):
        #    os.makedirs(self.filedir)

        self.srs = {'dev': None}
        self.lf = {'app': None}

        self.help_message = (
            "\n===================\n"
            "HELP"
            "\n===================\n"
            "To determine which serial ports are avilable for "
            "connected instruments, click "
            "'Menu --> Show available serial ports'."
            "\n===================\n"
            "To communicate with the SRS DG645 pulse generator, "
            "enter the serial port address (e.g. COM6) in the address "
            "field and use the checkbox to connect to the device. "
            "Adjust the pulse "
            "width, pulse delay, pulse maplitude, and number of "
            "pulses in the edit boxes. Then click 'Trigger pulses' "
            "to send pulses from the SRS. "
            "Uncheck the box to disconnect from the device."
            "\n===================\n"
            "To run the experimental sequence, click 'Run sequence' and "
            "'Abort sequence' to stop the sequence. "
            )
        self.ui.outbox.append(self.help_message)
    
    

    # %% ========= Princeton Instruments LightField control ==============



    def add_available_devices(self):
        # Add first available device and return
        for device in sio.experiment.AvailableDevices:
            self.ui.outbox.append('\n\tAdding Device...')
            sio.experimentexperiment.Add(device)
            return device

    '''
    def launch_lf_thread(self):
        """Launch LightField software in a new thread."""
        worker = Worker(self.launch_lf)  # pass other args here
        self.threadpool.start(worker)

    '''
    def launch_lf(self):
        """Launch LightField software."""
        # create a C# compatible List of type String object
        lf_exp_list = List[String]()
        # add the command line option for an empty experiment
        lf_exp_list.Add("/empty")
        # create the LightField Application (true for visible)
        # the 2nd parameter is the experiment name to load 
        self.lf['app'] = Automation(True, List[String](lf_exp_list))
        self.ui.acquire_raman.setEnabled(True)
        self.ui.set_raman_filename.setEnabled(True)
        self.ui.seq_raman_acquisition.setEnabled(True)

    def device_found(self, experiment):
        "Check if devices are connected to LightField."""
        for device in experiment.ExperimentDevices:
            if (device.Type == DeviceType.Camera):
                return True

    def save_file(self, filename, experiment):    
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
            ExperimentSettings.FileNameGenerationAttachDate, True)
        # Option to add time
        experiment.SetValue(
            ExperimentSettings.FileNameGenerationAttachTime, True)


    def acquire_raman(self):
        """Acquire Raman spectra using an opened instance of LightField."""
        # get current loaded experiment
        experiment = self.lf['app'].LightFieldApplication.Experiment
    
        # check for device and inform user if one is needed
        if (self.device_found(experiment)==True):        
            # check this location for saved spe after running
            _file_name = self.ui.set_raman_filename.text()
            # pass location of saved file
            self.save_file(_file_name, experiment)
            # acquire image
            experiment.Acquire()
            self.ui.outbox.append(
                    str(String.Format("{0} {1}",
                                "Image saved to",
                                experiment.GetValue(
                                    ExperimentSettings.
                                    FileNameGenerationDirectory))))
        else:
            self.ui.outbox.append('No LightField-compatible devices found.')
            




    # %% ============ SRS DG645 pulse generator control =================
    
    def pulsegen_on(self):
        "Run this function when pulse generator checkbox is checked."""
        if self.ui.pulsegen_on.isChecked():
            try:
                address = self.ui.pulsegen_address.text()
                dev = serial.Serial(port=address, timeout=2)
                dev.write('*IDN?\r'.encode())
                self.srs['dev'] = dev
                self.ui.outbox.append('Pulse generator connected.')
                self.ui.outbox.append(dev.readline().decode("utf-8"))
                self.ui.pulsegen_address.setEnabled(False)
                self.ui.config_pulse_frame.setEnabled(True)
                self.ui.seq_laser_trigger.setEnabled(True)
            except serial.SerialException:
                self.ui.outbox.append('Pulse generator could not connect.')
                self.ui.config_pulse_frame.setEnabled(False)
                self.ui.pulsegen_address.setEnabled(True)
                self.ui.pulsegen_on.setChecked(False)
                self.ui.seq_laser_trigger.setEnabled(False)
                self.srs['dev'] = None
        else: 
            try:
                self.srs['dev'].close()
            except AttributeError:
                pass
            self.srs['dev'] = None
            self.ui.outbox.append('Pulse generator closed.')
            self.ui.pulsegen_on.setChecked(False)
            self.ui.seq_laser_trigger.setEnabled(False)
        
    def trigger_pulses(self):
        """Fire a single burst of n pulses with spacing in seconds."""
        self.ui.trigger_pulses.setEnabled(False)
        # set pulse width in seconds
        pulse_width = self.ui.pulse_width.value()/1e3
        pulse_amplitude = self.ui.pulse_amplitude.value()
        pulse_delay = self.ui.pulse_delay.value()/1e3
        pulse_number = self.ui.pulse_number.value()
        self.ui.outbox.append('Triggering {} pulses...'.format(pulse_number))
        # set trigger source to single shot trigger
        self.srs['dev'].write('TSRC5\r'.encode())
        # set delay of A and B outputs
        self.srs['dev'].write(('DLAY2,0,'+str(0)+'\r').encode())
        self.srs['dev'].write(('DLAY3,2,'+str(pulse_width)+'\r').encode())
        # set amplitude of output A
        self.srs['dev'].write(('LAMP1,'+str(pulse_amplitude)+'\r').encode())
        for _ in range(pulse_number):
            # initiate single shot trigger
            self.srs['dev'].write('*TRG\r'.encode())
            time.sleep(pulse_delay)
        self.ui.trigger_pulses.setEnabled(True)
        self.ui.outbox.append('Pulse sequence complete.')


    def trigger_pulses_thread(self):
        """Trigger pulses in a new thread."""
        worker = Worker(self.trigger_pulses)  # pass other args here
        self.threadpool.start(worker)


    # %% ======= experimental sequence control functions =================

    def abort_seq(self):
        """Abort the expreimental sequence."""
        self.abort_seq = True


    def run_seq(self):
        """Run an experimental sequence."""
        self.ui.run_seq.setEnabled(False)
        self.ui.abort_seq.setEnabled(True)
        self.ui.set_seq_cycles.setEnabled(False)
        self.ui.outbox.append('Sequence initiated')
        
        tot_cycles = self.ui.set_seq_cycles.value()
        for c in range(tot_cycles):
            self.ui.outbox.append(
                    'running cycle {}/{}...'.format(c+1, tot_cycles))
            time.sleep(0.1)
            if self.abort_seq == True:
                self.ui.outbox.append('Sequence aborted.')
                break


            if self.ui.seq_laser_trigger.isChecked():
                print('checked triggering')
             
                
            if self.ui.seq_raman_acquisition.isChecked():
                print('checked acquisition')   
            

        self.abort_seq = False
        self.ui.run_seq.setEnabled(True)
        self.ui.abort_seq.setEnabled(False)
        self.ui.set_seq_cycles.setEnabled(True)
        self.ui.outbox.append('Sequence complete.')


    def run_seq_thread(self):
        """Run sequence in a new thread."""
        worker = Worker(self.run_seq)  # pass other args here
        self.threadpool.start(worker)



    # %% ============ system control functions =============================

    '''
    def view_file_save_dir(ops_dict):
        # Show the name of the file-saving directory in the output box on the GUI.
        try:  # if save file directory is already set
            ops_dict['output_box'].append('Current save file directory:')
            ops_dict['output_box'].append(ops_dict['save_file_dir'])
        except NameError:  # if file directory is not set
            ops_dict['output_box'].append(
                    'No save file directory has been set.')
            ops_dict['output_box'].append(
                    'Please set in File --> Change file save directory.')

    def set_file_save_directory(self):
        # set the directory for saving data files
        self.save_file_dir = str(QFileDialog.getExistingDirectory(
                self, 'Create or select directory for data files.'))
        self.ui.output_box.append('Save file directory set to:')
        self.ui.output_box.append(self.save_file_dir)

    def create_report(self):
        # Create Origin report of saved experimental data. This method
        # opens Origin, runs an internal Origin python script, imports
        # the saved data files, plots them, and saves the Origin file.
        Thread(target=ops.create_report, args=(self.ops_dict,)).start()

    def view_file_save_dir(self):
        # Print the file saving directory to the output box on GUI.
        ops.view_file_save_dir(self.keith_dict)

    '''



    def show_help(self):
        """Print help in the GUI output box."""
        self.ui.outbox.append(self.help_message)


    def print_ports(self):
        """Print a list of avilable serial ports."""
        ports = list(list_ports.comports())
        self.ui.outbox.append('Available serial ports:')
        for p in ports:    
            self.ui.outbox.append(str(p.device))


    def quitapp(self):
        """Quit the application."""
        if self.srs['dev'] != None:
            self.srs['dev'].close()
        self.deleteLater()
        # close app window
        self.close()  
        # kill python kernel
        sys.exit()  






    # =================== file I/O utilities =============================
    '''
    def export_results(self):
        """Save modeling results to file."""
        filename = 'QCMD_results'
        filepath = self.filedir + '\\' + filename + '.csv'
        df = pd.DataFrame(list(self.results.items()))
        df.to_csv(filepath)
        self.ui.outbox.append('\nFile saved to ' + filepath)


    def set_directory(self):
        """Set the directory for saving files."""
        self.filedir = str(QFileDialog.getExistingDirectory(
                self, 'Select a directory for storing data'))
        self.ui.outbox.append('\nFile directory is set to ' + self.filedir)


    def show_directory(self):
        """Show the file directory in the output box."""
        self.ui.outbox.append('\nFile directory is set to ' + self.filedir)


    def fit_model_in_new_thread(self):
        """Run Kelvin-Voigt model in new thread."""
        worker = Worker(self.fit_model)  # pass other args here
        self.threadpool.start(worker)


    def get_ui_inputs(self):
        """Get a dictionary of inputs from the UI."""
        uidict = {
                'f0': float(self.ui.f0.currentText())*1e6,
                'n': int(self.ui.n.currentText()),
                'rho': float(self.ui.film_density.value()),
                'h': float(self.ui.film_thickness.value())*1e-9,
                'medium': str(self.ui.medium.currentText()),
                'df_exp': float(self.ui.df_exp.value()),
                'dd_exp': float(self.ui.dd_exp.value()),
                'mu_low': int(self.ui.mu_exp_low.value()),
                'mu_high': int(self.ui.mu_exp_high.value()),
                'eta_low': int(self.ui.eta_exp_low.value()),
                'eta_high': int(self.ui.eta_exp_high.value())}
        return uidict


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


    def plot_setup(self, labels=['X', 'Y'], fsize=20, setlimits=False,
                   title=None, legend=False, colorbar=False,
                   limits=(0,1,0,1), save=False, filename='plot.jpg'):
        """Creates a custom plot configuration to make graphs look nice.
        This can be called with matplotlib for setting axes labels,
        titles, axes ranges, and the font size of plot labels.
        This should be called between plt.plot() and plt.show() commands."""
        plt.xlabel(str(labels[0]), fontsize=fsize)
        plt.ylabel(str(labels[1]), fontsize=fsize)
        fig = plt.gcf()
        fig.set_size_inches(6, 4)
        if title:
            plt.title(title, fontsize=fsize)
        if legend:
            plt.legend(fontsize=fsize-4)
        if setlimits:
            plt.xlim((limits[0], limits[1]))
            plt.ylim((limits[2], limits[3]))
        if colorbar:
            plt.colorbar()
        if save:
            fig.savefig(filename, dpi=120, bbox_inches='tight')
            plt.tight_layout()

    '''

# %% ====================== run application ===============================


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    window = App()
    window.show()
    sys.exit(app.exec_())