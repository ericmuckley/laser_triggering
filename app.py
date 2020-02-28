# -*- coding: utf-8 -*-

"""
GUI applicaton for automated control of laser processing procedures.
Instrument-specific modules are located in "my_libs" directory.

To see help, run this file to open the GUI,
then navigate to Menu --> Show Help.

Updated version of this application is stored at
https://github.com/ericmuckley/laser_triggering

Created on Feb 3 2020
@author: ericmuckley@gmail.com

"""

# --------------------- core GUI libraries --------------------------------
from PyQt5 import QtWidgets, uic, QtCore  # , QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog
import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt


# -------- import custom modules for contorlling instruments ---------------
from instr_libs import avacs  # Laseroptik AVACS beam attenuator
from instr_libs import srs  # SRS DG645 digital delay pulse generator
from instr_libs import mso  # Tektronix MSO64 oscilloscope
from instr_libs import kcube  # Thorlabs KDC101 stepper motor controllers
from instr_libs import ops  # for controlling operations of main GUI
from instr_libs import lf  # for controlling LightField Raman software
from instr_libs import mcl  # for controlling Marzhauser MCL-3 stage


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

        # create timer which updates fields on GUI (set interval in ms)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_gui_thread)
        self.timer.start(1500)  # int(self.ui.set_main_loop_delay.value()))

        # assign functions to top menu items
        # example: self.ui.menu_item_name.triggered.connect(self.func_name)
        self.ui.quit_app.triggered.connect(self.quitapp)
        self.ui.print_ports.triggered.connect(self.print_ports)
        self.ui.show_help.triggered.connect(ops.show_help)
        self.ui.show_log_path.triggered.connect(self.show_log_path)
        self.ui.show_file_list.triggered.connect(self.show_file_list)
        self.ui.plot_spectra.triggered.connect(self.plot_file_list)
        self.ui.export_settings.triggered.connect(self.export_settings)
        self.ui.import_settings.triggered.connect(self.import_settings)
        self.ui.set_filedir.triggered.connect(self.set_filedir)

        # assign actions to GUI buttons
        # example: self.ui.BUTTON_NAME.clicked.connect(self.FUNCTION_NAME)
        self.ui.trigger_pulses.clicked.connect(self.trigger_pulses_thread)
        self.ui.acquire_raman.clicked.connect(self.acquire_raman)
        self.ui.run_seq.clicked.connect(self.run_seq_thread)
        self.ui.abort_seq.clicked.connect(self.abort_seq)
        self.ui.launch_lf.clicked.connect(self.launch_lf_thread)
        self.ui.scope_acquire.clicked.connect(self.scope_acquire)
        self.ui.export_scope_trace.clicked.connect(self.export_scope_trace)
        self.ui.polarizer_on.clicked.connect(self.polarizer_on)
        self.ui.analyzer_on.clicked.connect(self.analyzer_on)
        self.ui.polarizer_home.clicked.connect(self.polarizer_home)
        self.ui.analyzer_home.clicked.connect(self.analyzer_home)
        self.ui.preview_grid_cords.clicked.connect(self.preview_grid_cords)

        # assign actions to checkboxes
        # example: self.ui.CHECKBOX.stateChanged.connect(self.FUNCTION_NAME)
        self.ui.pulsegen_on.stateChanged.connect(self.pulsegen_on)
        self.ui.mso_on.stateChanged.connect(self.mso_on)
        self.ui.avacs_on.stateChanged.connect(self.avacs_on)
        self.ui.mcl_on.stateChanged.connect(self.stage_on)


        # intialize log file for logging experimental settings
        self.filedir = os.getcwd()
        self.logdir = self.filedir + '\\logs\\'
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.starttime = time.strftime('%Y-%m-%d_%H-%M-%S')

        # intialize dictionaries for transporting GUI data to other modules
        self.ops = {
                'app': self.ui,
                'row_counter': 0,
                'logdir': self.logdir,
                'filedir': self.filedir,
                'outbox': self.ui.outbox,
                'starttime': self.starttime,
                'gui_update_finished': True,
                'data': np.full((1000, 11), '', dtype=object),
                'logpath': self.logdir+self.starttime+'.csv'}
        self.avacs = {
                'dev': None,
                'on': self.ui.avacs_on,
                'outbox': self.ui.outbox,
                'angle': self.ui.avacs_angle,
                'address': self.ui.avacs_address,
                'curr_angle': self.ui.current_avacs_angle}
        self.srs = {
                'dev': None,
                'tot_pulses': 0,
                'outbox': self.ui.outbox,
                'on': self.ui.pulsegen_on,
                'width': self.ui.pulse_width,
                'delay': self.ui.pulse_delay,
                'number': self.ui.pulse_number,
                'trigger': self.ui.trigger_pulses,
                'address': self.ui.pulsegen_address,
                'amplitude': self.ui.pulse_amplitude,
                'seq_laser_trigger': self.ui.seq_laser_trigger}
        self.mso = {
                'dev': None,
                'on': self.ui.mso_on,
                'logdir': self.logdir,
                'outbox': self.ui.outbox,
                'address': self.ui.mso_address,
                'acquire': self.ui.scope_acquire,
                'downsample': self.ui.mso_downsample,
                'export': self.ui.export_scope_trace}
        self.lf = {
                'app': None,
                'recent_file': None,
                'file_list': [],
                'outbox': self.ui.outbox,
                'acquire': self.ui.acquire_raman,
                'notes': self.ui.raman_filename_notes,
                'seq': self.ui.seq_raman_acquisition}
        self.kcube = {
                'pdev': None,
                'adev': None,
                'outbox': self.ui.outbox,
                'a_on': self.ui.analyzer_on,
                'p_on': self.ui.polarizer_on,
                'ahome': self.ui.analyzer_home,
                'phome': self.ui.polarizer_home,
                'aangle': self.ui.analyzer_angle,
                'pangle': self.ui.polarizer_angle,
                'rotation_end': self.ui.rotation_end,
                'aaddress': self.ui.analyzer_address,
                'paddress': self.ui.polarizer_address,
                'rotation_start': self.ui.rotation_start,
                'rotation_steps': self.ui.rotation_steps,
                'curr_pangle_label': self.ui.current_p_angle,
                'curr_aangle_label': self.ui.current_a_angle,
                'seq_polarizer_rot': self.ui.seq_polarizer_rot}
        self.mcl = {
               'dev': None,
               'on': self.ui.mcl_on,
               'prev_position': None,
               'outbox': self.ui.outbox,
               'seq_mcl': self.ui.seq_mcl,
               'set_x': self.ui.mcl_set_x,
               'set_y': self.ui.mcl_set_y,
               'address': self.ui.mcl_address,
               'show_x': self.ui.mcl_current_x,
               'show_y': self.ui.mcl_current_y,               
               'grid_xf': self.ui.mcl_grid_x_end,
               'grid_yf': self.ui.mcl_grid_y_end,
               'grid_xi': self.ui.mcl_grid_x_start,
               'grid_yi': self.ui.mcl_grid_y_start,
               'grid_xsteps': self.ui.mcl_grid_x_steps,
               'grid_ysteps': self.ui.mcl_grid_y_steps,
               'preview_grid_cords': self.ui.preview_grid_cords}

        # kill the process which opens LightField if its already running
        os.system("taskkill /f /im AddInProcess.exe")

        # initialize GUI settings by disabling buttons
        srs.enable_pulse_gen_buttons(self.srs, False)
        kcube.enable_polarizer(self.kcube, False)
        kcube.enable_analyzer(self.kcube, False)
        mcl.enable_stage(self.mcl, False)
        mso.enable_mso(self.mso, False)
        
        self.items_to_deactivate = [
                self.ui.abort_seq,
                self.ui.avacs_angle,
                self.ui.acquire_raman,
                self.ui.seq_raman_acquisition]
        [i.setEnabled(False) for i in self.items_to_deactivate]

    # %% ======= experimental sequence control functions =================

    def run_seq(self):
        """Run an experimental sequence."""
        self.initialize_sequence()
        
        
        
        # get MCL-3 stage grid coordinates
        if self.ui.seq_mcl.isChecked():
            grid = mcl.get_grid(self.mcl)
            self.ui.outbox.append(str(grid))
        else:
            grid = np.array([[0,0]])
            
        
        # loop over each location on the grid of stage positions
        for gi, g in enumerate(grid):
            self.ui.outbox.append(
                'Setting grid position {}/{} ({})'.format(gi+1,len(grid),g))
            
            
            # get x and y coordinates
            x, y = g 
            self.mcl['set_x'].setValue(x)
            self.mcl['set_y'].setValue(y)
            
            time.sleep(10)
            
            
            #  get polarizer angles or use current angle
            if self.ui.seq_polarizer_rot.isChecked():
                polarizer_angles = kcube.get_angle_steps(self.kcube)
            else:
                polarizer_angles = [self.ui.polarizer_angle.value()]
    

            if self.ui.seq_raman_acquisition.isChecked(): 
                # loop over each polarizer angle and acquire initial Raman spectra
                for a in polarizer_angles:
                    if self.abort_seq is True:
                        self.ui.outbox.append('Sequence aborted.')
                        break
                    if self.ui.seq_polarizer_rot.isChecked():
                        self.ui.outbox.append('polarizer angle: {}'.format(a))
                        self.ui.polarizer_angle.setValue(a)
                        time.sleep(2)
                        while kcube.p_in_motion(self.kcube):
                            time.sleep(1)
                    if self.ui.seq_raman_acquisition.isChecked():
                        self.acquire_raman()
                    self.log_to_file()
                    time.sleep(self.ui.pause_between_cycles.value())
    
    
    
            # loop over each experimental cycle
            tot_cycles = self.ui.set_seq_cycles.value()
            for c in range(tot_cycles):  
                self.ui.outbox.append('cycle {}/{}'.format(c+1, tot_cycles))
                if self.abort_seq is True:
                    break
    
                # trigger laser pulses from pulse generator
                if self.ui.seq_laser_trigger.isChecked():
                    self.trigger_pulses()
                    time.sleep(0.1)
    
                # loop over each polarizer angle and acquire Raman spectrum
                for a in polarizer_angles:
                    if self.abort_seq is True:
                        self.ui.outbox.append('Sequence aborted.')
                        break
                    if self.ui.seq_polarizer_rot.isChecked():
                        self.ui.outbox.append('polarizer angle: {}'.format(a))
                        self.ui.polarizer_angle.setValue(a)
                        time.sleep(2)
                        while kcube.p_in_motion(self.kcube):
                            time.sleep(1)
                    if self.ui.seq_raman_acquisition.isChecked():
                        self.acquire_raman()
                    self.log_to_file()
                    time.sleep(self.ui.pause_between_cycles.value())

        self.finalize_sequence()


    def initialize_sequence(self):
        """Initialize settings when an experimental sequence starts."""
        self.ui.run_seq.setEnabled(False)
        self.ui.abort_seq.setEnabled(True)
        self.ui.set_seq_cycles.setEnabled(False)
        self.ui.pause_between_cycles.setEnabled(False)
        self.ui.seq_laser_trigger.setEnabled(False)
        self.ui.seq_polarizer_rot.setEnabled(False)
        self.ui.seq_raman_acquisition.setEnabled(False)
        self.ui.rotation_end.setEnabled(False)
        self.ui.rotation_start.setEnabled(False)
        self.ui.rotation_steps.setEnabled(False)
        self.ui.seq_mcl.setEnabled(False)
        self.ui.outbox.append('Sequence initiated')

    def finalize_sequence(self):
        """Finalize settings when an experimental sequence ends."""
        self.abort_seq = False
        self.ui.run_seq.setEnabled(True)
        self.ui.abort_seq.setEnabled(False)
        self.ui.set_seq_cycles.setEnabled(True)
        self.ui.pause_between_cycles.setEnabled(True)
        self.ui.seq_laser_trigger.setEnabled(True)
        self.ui.seq_polarizer_rot.setEnabled(True)
        self.ui.seq_raman_acquisition.setEnabled(True)
        self.ui.rotation_end.setEnabled(True)
        self.ui.rotation_start.setEnabled(True)
        self.ui.rotation_steps.setEnabled(True)
        self.ui.seq_mcl.setEnabled(True)
        self.ui.outbox.append('Sequence complete.')

    def run_seq_thread(self):
        """Run sequence in a new thread."""
        worker = Worker(self.run_seq)  # pass other args here
        self.threadpool.start(worker)

    def abort_seq(self):
        """Abort the expreimental sequence."""
        self.abort_seq = True


    # %% ========= Thorlabs KDC101 servo motor controllers= ==============    

    def stage_on(self):
        """Checkbox for MCL stage controller is checked/unchecked."""
        mcl.stage_on(self.mcl)
    
    def preview_grid_cords(self):
        """Preview the grid coordinates."""
        mcl.preview_grid_cords(self.mcl)

    '''
    def stage_on_thread(self):
        """Connect to stage in a new thread."""
        worker = Worker(self.stage_on)  # pass other args here
        self.threadpool.start(worker)
    '''


    # %% ========= Thorlabs KDC101 servo motor controllers= ==============

    def analyzer_on(self):
        """Checkbox for analyzer controller is checked/unchecked."""
        kcube.analyzer_on(self.kcube)

    def polarizer_on(self):
        """Checkbox for polarizer controller is checked/unchecked."""
        kcube.polarizer_on(self.kcube)

    def analyzer_move_to(self):
        """Move the analyzer to specified angle."""
        kcube.analyzer_move_to(self.kcube)

    def polarizer_move_to(self):
        """Move the polarizer to specified angle."""
        kcube.polarizer_move_to(self.kcube)

    def polarizer_home(self):
        """Move the polarizer to its home position."""
        kcube.polarizer_home(self.kcube)

    def analyzer_home(self):
        """Move the analizer to its home position."""
        kcube.analyzer_home(self.kcube)



    # %% ========= Princeton Instruments LightField control ==============

    def launch_lf_thread(self):
        """Launch LightField software in a new thread."""
        worker = Worker(self.launch_lf)  # pass other args here
        self.threadpool.start(worker)

    def launch_lf(self):
        """Launch LightField software."""
        self.ui.outbox.append('Opening LightField...')
        lf.launch_lf(self.lf)

    def show_file_list(self):
        """Show the list of acquired Raman spe files."""
        lf.show_file_list(self.lf)

    def acquire_raman(self):
        """Acquire Raman spectra using an opened instance of LightField."""
        lf.acquire_raman(self.lf)

    def plot_file_list(self):
        """Plot the Raman acquisition spectra. They should be in csv
        format as specified by the Default_Python_Experiment file
        in LightField."""
        lf.plot_file_list(self.lf)

    # %% ========= Tektronix MSO64 mixed signal oscilloscope ==============

    def mso_on(self):
        "Run this function when MSO64 oscilloscope checkbox is checked."""
        mso.mso_on(self.mso)

    def scope_acquire(self):
        """Acquire and plot signal from oscilloscope."""
        mso.acquire(self.mso)

    def export_scope_trace(self):
        """Export most recent oscilloscope trace to file."""
        mso.export(self.mso)

    # %% ============ SRS DG645 pulse generator control =================

    def pulsegen_on(self):
        "Run this function when pulse generator checkbox is checked."""
        srs.pulsegen_on(self.srs)

    def trigger_pulses(self):
        """Fire a single burst of n pulses with spacing in seconds."""
        srs.trigger_pulses(self.srs)

    def trigger_pulses_thread(self):
        """Trigger pulses in a new thread."""
        worker = Worker(self.trigger_pulses)  # pass other args here
        self.threadpool.start(worker)

    # %% ============ Laseroptik AVACS beam attenuator ===================

    def avacs_on(self):
        """Laseroptik beam attenuator checkbox is checked/unchecked."""
        avacs.avacs_on(self.avacs)

    # %% ============ system control functions =============================

    def update_gui_thread(self):
        """Update the GUI objects in a new thread."""
        if self.ops['gui_update_finished']:
            self.ops['gui_update_finished'] = False
            worker = Worker(self.update_gui)  # pass other args here
            self.threadpool.start(worker)

    def update_gui(self):
        """Function to execute on a regularly based on timer. Use this
        for continuously updating GUI objects."""
        # update current polarizer and analyzer angles on GUI
        if self.kcube['pdev'] is not None:
            kcube.polarizer_move_to(self.kcube)
        if self.kcube['adev'] is not None:
            kcube.analyzer_move_to(self.kcube)
        if self.avacs['dev'] is not None:
            avacs.update_angle(self.avacs)
        # update stage position on the GUI
        if self.mcl['dev'] is not None:
            mcl.update_position(self.mcl)
        self.ops['gui_update_finished'] = True 


    def set_filedir(self):
        # set the directory for saving data files
        self.ops['logdir'] = str(QFileDialog.getExistingDirectory(
                self, 'Create or select directory for data files.'))
        self.ui.outbox.append('Save file directory set to:')
        self.ui.outbox.append(self.ops['logdir'])

    def export_settings(self):
        """Export all GUI settings to file."""
        ops.export_settings(self.ops)

    def import_settings(self):
        """Import all GUI settings from file."""
        import_settings_filepath = QFileDialog.getOpenFileName(
                self, 'Select experiment settings file', '.ini')[0]
        ops.import_settings(self.ops, import_settings_filepath)

    def show_log_path(self):
        """Show the path to the log file."""
        self.ui.outbox.append('Log file path: %s' % (self.ops['logpath']))

    def log_to_file(self):
        """Create log file."""
        ops.log_to_file(self.ops, self.srs, self.lf, self.kcube, self.mcl)

    def print_ports(self):
        """Print a list of available serial and VISA ports."""
        ops.print_ports(self.ops)

    def quitapp(self):
        """Quit the application."""
        if self.srs['dev']:
            self.srs['dev'].close()
        if self.mso['dev']:
            self.mso['dev'].close()
        if self.avacs['dev']:
            self.avacs['dev'].close()
        if self.mcl['dev']:
            self.mcl['dev'].close()
        # kill the process which opens LightField if its already running
        # os.system("taskkill /f /im AddInProcess.exe")
        # stop timer
        self.timer.stop()
        # close app window and kill python kernel
        self.deleteLater()
        self.close()
        #sys.exit()

# %% ====================== run application ===============================

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    window = App()
    window.show()
    sys.exit(app.exec_())
