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
from PyQt5 import QtWidgets, uic, QtCore#, QtGui
from PyQt5.QtWidgets import QMainWindow#, QFileDialog
#from PyQtCore import QRunnable, QThreadPool, pyqtSlot
import os
import sys
import time
import serial
import visa
from serial.tools import list_ports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

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

# ------- change matplotlib settings to make plots look nicer --------------
plt.rcParams['xtick.labelsize'] = 20
plt.rcParams['ytick.labelsize'] = 20
plt.rcParams['axes.linewidth'] = 3
plt.rcParams['xtick.minor.width'] = 3
plt.rcParams['xtick.major.width'] = 3
plt.rcParams['ytick.minor.width'] = 3
plt.rcParams['ytick.major.width'] = 3
plt.rcParams['figure.autolayout'] = True


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
        self.ui.quit_app.triggered.connect(self.quitapp)
        self.ui.print_ports.triggered.connect(self.print_ports)
        self.ui.show_help.triggered.connect(self.show_help_popup)
        self.ui.show_log_path.triggered.connect(self.show_log_path)
        self.ui.show_file_list.triggered.connect(self.show_file_list)
        self.ui.plot_spectra.triggered.connect(self.plot_file_list)
        
        
        # assign actions to GUI buttons
        # example: self.ui.BUTTON_NAME.clicked.connect(self.FUNCTION_NAME)
        self.ui.trigger_pulses.clicked.connect(self.trigger_pulses_thread)
        self.ui.acquire_raman.clicked.connect(self.acquire_raman)
        self.ui.run_seq.clicked.connect(self.run_seq_thread)
        self.ui.abort_seq.clicked.connect(self.abort_seq)
        self.ui.launch_lf.clicked.connect(self.launch_lf_thread)
        self.ui.scope_acquire.clicked.connect(self.scope_acquire)
        
        
        # assign actions to checkboxes
        # example: self.ui.CHECKBOX.stateChanged.connect(self.FUNCTION_NAME)
        self.ui.pulsegen_on.stateChanged.connect(self.pulsegen_on)
        self.ui.mso_on.stateChanged.connect(self.mso_on)
        
        
        # intialize log file for logging experimental settings
        self.filedir = os.getcwd()+'\\logs'
        if not os.path.exists(self.filedir):
            os.makedirs(self.filedir)
        self.starttime = time.strftime('%Y-%m-%d_%H-%M-%S')
        self.log = {
                'path': self.filedir+'\\'+self.starttime+'.csv',
                'row_counter': 0,
                'data': np.full((1000, 7), '', dtype=object)}

        
        # intialize instances of software and instruments
        self.mso = {'dev': None}
        self.srs = {'dev': None, 'tot_pulses': 0}
        self.lf = {'app': None, 'recent_file': None,
                   'file_list': []}


        # kill the process which opens LightField if its already running
        os.system("taskkill /f /im AddInProcess.exe")
        
        
        self.ui.pulse_gen_frame.setEnabled(False)
        self.ui.abort_seq.setEnabled(False)
        self.ui.acquire_raman.setEnabled(False)
        self.ui.seq_raman_acquisition.setEnabled(False)
        self.ui.seq_laser_trigger.setEnabled(False)
        self.ui.scope_acquire.setEnabled(False)
        self.ui.mso_downsample.setEnabled(False)





    # %% ========= Princeton Instruments LightField control ==============


    def launch_lf_thread(self):
        """Launch LightField software in a new thread."""
        worker = Worker(self.launch_lf)  # pass other args here
        self.threadpool.start(worker)

    
    def launch_lf(self):
        """Launch LightField software."""
        # kill the process which opens LightField if its already running
        os.system("taskkill /f /im AddInProcess.exe")
        # create a C# compatible List of type String object
        lf_exp_list = List[String]()
        # add the command line option for an empty experiment
        lf_exp_list.Add("Default_Python_Experiment")#("/empty")
        # create the LightField Application (true for visible)
        # the 2nd parameter is the experiment name to load 
        self.lf['app'] = Automation(True, List[String](lf_exp_list))
        self.ui.acquire_raman.setEnabled(True)
        self.ui.raman_filename_notes.setEnabled(True)
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
            ExperimentSettings.FileNameGenerationAttachDate, False)
        # Option to add time
        experiment.SetValue(
            ExperimentSettings.FileNameGenerationAttachTime, False)


    def show_file_list(self):
        """Show the list of acquired Raman spe files."""
        self.ui.outbox.append(
                '\n{} Raman acquisition files'.format(
                        len(self.lf['file_list'])))
        for f in self.lf['file_list']:
            self.ui.outbox.append(f)



    def acquire_raman(self):
        """Acquire Raman spectra using an opened instance of LightField."""
        # get current loaded experiment
        experiment = self.lf['app'].LightFieldApplication.Experiment
    
        # check for device and inform user if one is needed
        if (self.device_found(experiment)==True):        
            # check this location for saved spe after running
            notes = self.ui.raman_filename_notes.text().replace(',','__')
            file_name = time.strftime('%Y-%m-%d_%H-%M-%S')+'_'+notes
            self.lf['recent_file'] = file_name
            self.lf['file_list'].append(file_name+'.csv')
            # pass location of saved file
            self.save_file(file_name, experiment)
            # acquire image
            experiment.Acquire()
            self.ui.outbox.append(
                    str(String.Format("{0} {1}", "Data saved to",
                                experiment.GetValue(
                                    ExperimentSettings.
                                    FileNameGenerationDirectory))))
        else:
            self.ui.outbox.append(
                    '\nNo LightField-compatible devices found.')



    def plot_file_list(self):
        """Plot the Raman acquisition spectra. They should be in csv
        format as specified by the Default_Python_Experiment file
        in LightField."""
        if len(self.lf['file_list']) > 0:
            p='C:\\Users\\Administrator\\Documents\\LightField\\csv_files\\'
            colors = cm.jet(np.linspace(0, 1, len(self.lf['file_list'])))
            plt.ion()
            fig = plt.figure(0)
            fig.clf()
            for fi, f in enumerate(self.lf['file_list']):
                df = pd.read_csv(p+str(f))
                plt.plot(df['Wavelength'], df['Intensity'], label=fi,
                         c=colors[fi], lw=1)
            self.plot_setup(labels=('Wavelength (nm)', 'Intensity (counts)'))
            plt.legend()
            fig.canvas.set_window_title('Spectra')
            plt.draw()








  # %% ========= Tektronix MSO64 mixed signal oscilloscope ==============


    def mso_on(self):
        "Run this function when MSO64 oscilloscope checkbox is checked."""
        if self.ui.mso_on.isChecked():
            try:
                rm = visa.ResourceManager()
                dev = rm.open_resource(self.ui.mso_address.text())
                self.mso['dev'] = dev
                self.ui.outbox.append('Oscilloscope connected.')
                self.ui.outbox.append(dev.query('*IDN?'))
                self.ui.scope_acquire.setEnabled(True)
                self.ui.mso_address.setEnabled(False)
                self.ui.mso_downsample.setEnabled(True)
            except visa.VISAIOERROR:
                self.ui.outbox.append('Oscilloscope could not connect.')
                self.ui.mso_address.setEnabled(True)
                self.ui.pulsegen_on.setChecked(False)
                self.ui.scope_acquire.setEnabled(False)
                self.ui.mso_downsample.setEnabled(False)
                self.mso['dev'] = None
        if not self.ui.mso_on.isChecked():
            try:
                self.mso['dev'].close()
            except AttributeError:
                pass
            self.mso['dev'] = None
            self.ui.outbox.append('Oscilloscope closed.')
            self.ui.mso_address.setEnabled(True)
            self.ui.mso_on.setChecked(False)
            self.ui.scope_acquire.setEnabled(False)
            self.ui.mso_downsample.setEnabled(False)


    def get_scope_timescale(self, signal, downsample=10):
        """Get the time-scale associated with the scope signal."""
        # get time-scale increment
        dt = float(self.mso['dev'].query('WFMOutpre:XINcr?'))
        # calculate the actual values of the x-scale
        t_scale = np.linspace(0, len(signal)*downsample*dt,
                              num=int(len(signal)))
        return t_scale


    def scope_acquire(self):
        """Acquire and plot signal on oscilloscope."""
        self.mso['dev'].write(':DATA:SOURCE CH1')
        self.mso['dev'].write(':DATa:START 1')
        self.mso['dev'].write(':DATa:STOP 12500000')
        #dev.write('WFMOutpre:NR_PT 100000')
        self.mso['dev'].write(':WFMOutpre:ENCDG ASCII')
        self.mso['dev'].write(':WFMOOutpre:BYT_NR 1')
        #dev.write(':HEADER 0')
        
        
        
        
        downsample = self.ui.mso_downsample.value()
        
        signal_raw = np.array(dev.query(':CURVE?').split(','))
        signal = signal_raw.astype(float)[::downsample]
        
        
        
        timescale = get_scope_timescale(signal, downsample=downsample)
        
        
        #signalmso['dev'].query('WFMOutpre:WFId?'))
        '''
        
        
        

        
        
        plt.plot(time_scale, signal, lw=0.5)
        fig = plt.gcf()
        fig.set_size_inches(15,6)
        plt.show()

        
        signal_raw = np.array(dev.query(':CURVE?').split(','))
        signal = signal_raw.astype(float)[::downsample]
        '''



    # %% ============ SRS DG645 pulse generator control =================
    
    def pulsegen_on(self):
        "Run this function when pulse generator checkbox is checked."""
        if self.ui.pulsegen_on.isChecked():
            try:
                dev = serial.Serial(
                        port=self.ui.pulsegen_address.text(),
                        timeout=2)
                dev.write('*IDN?\r'.encode())
                self.srs['dev'] = dev
                self.ui.outbox.append('\nPulse generator connected.')
                self.ui.outbox.append(dev.readline().decode("utf-8"))
                self.ui.pulsegen_address.setEnabled(False)
                self.ui.pulse_gen_frame.setEnabled(True)
                self.ui.seq_laser_trigger.setEnabled(True)
            except serial.SerialException:
                self.ui.outbox.append('\nPulse generator could not connect.')
                self.ui.pulse_gen_frame.setEnabled(False)
                self.ui.pulsegen_address.setEnabled(True)
                self.ui.pulsegen_on.setChecked(False)
                self.ui.seq_laser_trigger.setEnabled(False)
                self.srs['dev'] = None
        if not self.ui.pulsegen_on.isChecked():
            try:
                self.srs['dev'].close()
            except AttributeError:
                pass
            self.srs['dev'] = None
            self.ui.outbox.append('\nPulse generator closed.')
            self.ui.pulsegen_address.setEnabled(True)
            self.ui.pulsegen_on.setChecked(False)
            self.ui.seq_laser_trigger.setEnabled(False)
            self.ui.pulse_gen_frame.setEnabled(False)
            self.ui.seq_laser_trigger.setEnabled(False)
            
        
    def trigger_pulses(self):
        """Fire a single burst of n pulses with spacing in seconds."""
        self.ui.trigger_pulses.setEnabled(False)
        # set pulse width in seconds
        pulse_width = self.ui.pulse_width.value()/1e3
        pulse_amplitude = self.ui.pulse_amplitude.value()
        pulse_delay = self.ui.pulse_delay.value()/1e3
        pulse_number = self.ui.pulse_number.value()
        self.ui.outbox.append('\nTriggering {} pulses...'.format(pulse_number))
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
        self.srs['tot_pulses'] += pulse_number


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
        self.ui.outbox.append('\nSequence initiated')
        
        tot_cycles = self.ui.set_seq_cycles.value()
        for c in range(tot_cycles):
            self.ui.outbox.append(
                    'running cycle {}/{}...'.format(c+1, tot_cycles))
            if self.abort_seq == True:
                self.ui.outbox.append('Sequence aborted.')
                break
            if self.ui.seq_laser_trigger.isChecked():
                self.trigger_pulses()
                time.sleep(0.1)
                
            if self.ui.seq_raman_acquisition.isChecked():
                self.acquire_raman()

            self.log_to_file()
            time.sleep(self.ui.pause_between_cycles.value())
            
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

    
    def plot_setup(self, labels=['X', 'Y'], fsize=20, setlimits=False,
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




    def show_help_popup(self):
        """Show the help popup message."""
        self.help_message = (
            "HELP"
            "\n=========================================================\n"
            "Click 'Menu --> Show available serial ports' to check "
            "available ports. "
            "To communicate with the SRS DG645 pulse generator, "
            "enter the serial port address (e.g. COM6) in the address "
            "field and use the checkbox to connect to the device. "
            "Adjust the pulse "
            "width, pulse delay, pulse maplitude, and number of "
            "pulses in the edit boxes. Then click 'Trigger pulses' "
            "to send pulses from the SRS. "
            "Uncheck the box to disconnect from the device."
            "\n=========================================================\n"
            "To configure LightField, first open LightField by "
            "clicking 'Launch LightField.' Then configure all desired "
            "settings inside LightField. To acquire, click 'Acquire'. "
            "\n=========================================================\n"
            "To run the experimental sequence, check boxes for the "
            "pulse triggering and acquisition. Then click 'Run sequence'. "
            "Click 'Abort sequence' to stop the sequence prematurely."
            "\n=========================================================\n"
            )
        self.help_popup = QtWidgets.QMessageBox()
        self.help_popup.setWindowTitle('Help')
        self.help_popup.setText(self.help_message)
        self.help_popup.exec_()


    def show_log_path(self):
        """Show the path to the log file."""
        self.ui.outbox.append('\nLog file path: %s' %(self.log['path']))


    def get_log_row_data(self):
        """Get data for the most recent row of the log file."""
        d = {'time': time.strftime('%Y-%m-%d_%H-%M-%S'),
             'total_pulses': self.srs['tot_pulses'],
             'pulsewidth_ms':  self.ui.pulse_width.value()/1e3,
             'pulse_amplitude_V': self.ui.pulse_amplitude.value(),
             'pulse_delay_ms': self.ui.pulse_delay.value()/1e3,
             'pulse_number': self.ui.pulse_number.value(),
             'recent_file': self.lf['recent_file']}
        return d


    def log_to_file(self):
        """Create log file."""
        # get most recent row of data
        d = self.get_log_row_data()
        # assign most recent row to last row in log data
        self.log['data'][self.log['row_counter']] = list(d.values())
        # convert log dtaa to Pandas DataFrame
        df = pd.DataFrame(columns=list(d.keys()),
                              data=self.log['data'])
        # remove empty rows before saving
        df.replace('', np.nan, inplace=True)
        df.dropna(how='all', inplace=True)
        # save dataframe as csv file
        df.to_csv(self.log['path'], index=False)
        self.ui.outbox.append('\nLog file appended.')
        self.log['row_counter'] += 1



    def print_ports(self):
        """Print a list of available serial and VISA ports."""
        rm = visa.ResourceManager()
        visa_ports = list(rm.list_resources())
        serial_ports = list(list_ports.comports())
        self.ui.outbox.append('Available instrument addresses:')
        [self.ui.outbox.append(str(p)) for p in visa_ports]
        [self.ui.outbox.append(str(p.device)) for p in serial_ports]
        

    def quitapp(self):
        """Quit the application."""
        # close instances of all instruments
        self.srs['dev'].close()
        self.mso['dev'].close()
        # kill the process which opens LightField if its already running
        #os.system("taskkill /f /im AddInProcess.exe")
        self.deleteLater()
        # close app window
        self.close()  
        # kill python kernel
        sys.exit()  
 
    
    '''

    def set_directory(self):
        """Set the directory for saving files."""
        self.filedir = str(QFileDialog.getExistingDirectory(
                self, 'Select a directory for storing data'))
        self.ui.outbox.append('\nFile directory is set to ' + self.filedir)


    def show_directory(self):
        """Show the file directory in the output box."""
        self.ui.outbox.append('\nFile directory is set to ' + self.filedir)



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




# %% ====================== run application ===============================


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    window = App()
    window.show()
    sys.exit(app.exec_())