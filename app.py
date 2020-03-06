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

import os
import sys
import time
import numpy as np
#import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, uic, QtCore  # , QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog

# -------- import custom modules for controlling instruments ---------------

from instr_libs import avacs  # Laseroptik AVACS beam attenuator
from instr_libs import srs  # SRS DG645 digital delay pulse generator
from instr_libs import mso  # Tektronix MSO64 oscilloscope
from instr_libs import kcube  # Thorlabs KDC101 stepper motor controllers
from instr_libs import ops  # for controlling operations of main GUI
from instr_libs import lf  # for controlling LightField Raman software
from instr_libs import mcl  # for controlling Marzhauser MCL-3 stage
from instr_libs import piline  # for controlling PI C-867 PILine rotator


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

        # create application instance
        super(App, self).__init__()
        self.ui = App.Ui_MainWindow()
        self.ui.setupUi(self)

        # initialize multithreading
        self.threadpool = QtCore.QThreadPool()

        # create timer which updates fields on GUI (set interval in ms)
        #self.timer = QtCore.QTimer(self)
        #self.timer.timeout.connect(self.update_gui_thread)
        #self.timer.start(500)

        # assign actions to top menu items
        # example: self.ui.menu_item_name.triggered.connect(self.func_name)
        self.ui.quit_app.triggered.connect(self.quitapp)
        self.ui.show_help.triggered.connect(ops.show_help)
        self.ui.set_filedir.triggered.connect(self.set_filedir)
        self.ui.print_ports.triggered.connect(self.print_ports)
        self.ui.plot_spectra.triggered.connect(self.plot_file_list)
        self.ui.show_log_path.triggered.connect(self.show_log_path)
        self.ui.show_file_list.triggered.connect(self.show_file_list)
        self.ui.export_settings.triggered.connect(self.export_settings)
        self.ui.import_settings.triggered.connect(self.import_settings)
        
        # assign actions to GUI buttons
        # example: self.ui.BUTTON_NAME.clicked.connect(self.FUNCTION_NAME)
        self.ui.abort_seq.clicked.connect(self.abort_seq)
        self.ui.run_seq.clicked.connect(self.run_seq_thread)
        self.ui.analyzer_on.clicked.connect(self.analyzer_on)
        self.ui.polarizer_on.clicked.connect(self.polarizer_on)
        self.ui.launch_lf.clicked.connect(self.launch_lf_thread)
        self.ui.scope_acquire.clicked.connect(self.scope_acquire)
        self.ui.acquire_raman.clicked.connect(self.acquire_raman)
        self.ui.analyzer_set_now.clicked.connect(self.analyzer_set_now)
        self.ui.polarizer_set_now.clicked.connect(self.polarizer_set_now)
        self.ui.trigger_pulses.clicked.connect(self.trigger_pulses_thread)
        self.ui.export_scope_trace.clicked.connect(self.export_scope_trace)
        self.ui.preview_grid_cords.clicked.connect(self.preview_grid_cords)
        self.ui.piline_set_now.clicked.connect(self.piline_set_now_thread)
        self.ui.piline_preview.clicked.connect(self.piline_preview)
        self.ui.avacs_set_now.clicked.connect(self.avacs_set_now_thread)
        self.ui.mcl_set_now.clicked.connect(self.mcl_set_now_thread)
        self.ui.polarizer_set_now.clicked.connect(self.p_set_now_thread)
        self.ui.analyzer_set_now.clicked.connect(self.a_set_now_thread)


        # assign actions to checkboxes
        # example: self.ui.CHECKBOX.stateChanged.connect(self.FUNCTION_NAME)
        self.ui.mso_on.stateChanged.connect(self.mso_on)
        self.ui.mcl_on.stateChanged.connect(self.mcl_on_thread)
        self.ui.avacs_on.stateChanged.connect(self.avacs_on_thread)
        self.ui.pulsegen_on.stateChanged.connect(self.pulsegen_on)
        self.ui.piline_on.stateChanged.connect(self.piline_on_thread)
        
        # assign actions to user input fields (text and numeric)
        # example: self.ui.TEXT_FIELD.textChanged.connect(self.FUNCTION_NAME)
        # example: self.ui.SPIN_BOX.valueChanged.connect(self.FUNCTION_NAME)      
        

        # intialize log file for logging experimental settings
        self.filedir = os.getcwd()
        self.logdir = self.filedir + '\\logs\\'
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.starttime = time.strftime('%Y-%m-%d_%H-%M-%S')    
        
        # information related to operations of the application
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
    
        # information related to Laseroptik beam attenuator
        self.avacs = {
                'dev': None,
                'on': self.ui.avacs_on,
                'outbox': self.ui.outbox,
                'set': self.ui.avacs_set,
                'address': self.ui.avacs_address,
                'set_now': self.ui.avacs_set_now,
                'display': self.ui.avacs_display}
        
        # information related to SRS DG645 digital delay pulse generator
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
        
        # information related to Tektronix MSO64 oscilloscope
        self.mso = {
                'dev': None,
                'on': self.ui.mso_on,
                'logdir': self.logdir,
                'outbox': self.ui.outbox,
                'address': self.ui.mso_address,
                'acquire': self.ui.scope_acquire,
                'downsample': self.ui.mso_downsample,
                'export': self.ui.export_scope_trace}
        
        # information related to Princeton Instruments LightField software
        self.lf = {
                'app': None,
                'recent_file': None,
                'file_list': [],
                'outbox': self.ui.outbox,
                'acquire': self.ui.acquire_raman,
                'notes': self.ui.raman_filename_notes,
                'seq': self.ui.seq_raman_acquisition}

        # information related to Thorlabs K-Cube KDC101 rotation controllers
        self.kcube = {
                'pdev': None,
                'adev': None,
                'outbox': self.ui.outbox,
                'a_on': self.ui.analyzer_on,
                'p_on': self.ui.polarizer_on,
                'a_set_now': self.ui.analyzer_set_now,
                'p_set_now': self.ui.polarizer_set_now,
                'a_set': self.ui.analyzer_set,
                'p_set': self.ui.polarizer_set,
                'rotation_end': self.ui.rotation_end,
                'aaddress': self.ui.analyzer_address,
                'paddress': self.ui.polarizer_address,
                'rotation_start': self.ui.rotation_start,
                'rotation_steps': self.ui.rotation_steps,
                'p_display': self.ui.polarizer_display,
                'a_display': self.ui.analyzer_display,
                'seq_polarizer_rot': self.ui.seq_polarizer_rot}

        # information related to Marzhauser MCL-3 X-Y stage
        self.mcl = {
               'dev': None,
               'on': self.ui.mcl_on,
               'outbox': self.ui.outbox,
               'seq_mcl': self.ui.seq_mcl,
               'set_x': self.ui.mcl_set_x,
               'set_y': self.ui.mcl_set_y,
               'set_now': self.ui.mcl_set_now,
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

        # information related to PILine PI C-867 rotation stage controller
        self.piline = {
            'dev': None,
            'on': self.ui.piline_on,
            'outbox': self.ui.outbox,
            'set': self.ui.piline_set,
            'seq': self.ui.seq_piline,
            'initial': self.ui.piline_initial,
            'final': self.ui.piline_final,
            'steps': self.ui.piline_steps,
            'preview': self.ui.piline_preview,
            'set_now': self.ui.piline_set_now,
            'display': self.ui.piline_display,
            'address': self.ui.piline_address}

        # kill the process which opens LightField if its already running
        os.system("taskkill /f /im AddInProcess.exe")

        # disable GUI buttons for instruments which are not connected
        srs.enable_srs(self.srs, False)
        kcube.enable_polarizer(self.kcube, False)
        kcube.enable_analyzer(self.kcube, False)
        mcl.enable_stage(self.mcl, False)
        mso.enable_mso(self.mso, False)
        piline.enable_piline(self.piline, False)
        avacs.enable_avacs(self.avacs, False)
        self.items_to_deactivate = [
                self.ui.abort_seq,
                self.ui.acquire_raman,
                self.ui.seq_raman_acquisition]
        [i.setEnabled(False) for i in self.items_to_deactivate]



    # %% ============ PI C-867 PILine rotation controller ================

    def piline_on(self):
        """Checkbox for piline is checked/unchecked."""
        piline.piline_on(self.piline)

    def piline_on_thread(self):
        """Connect to PI C-867 PILine in a new thread."""
        worker = Worker(self.piline_on)  # pass other args here
        self.threadpool.start(worker)

    def piline_set_now_thread(self):
        """Move the piline stage in a new thread."""
        worker = Worker(self.piline_set_now)  # pass other args here
        self.threadpool.start(worker)

    def piline_set_now(self):
        """Move the piline stage."""
        piline.move(self.piline)
        
    def piline_preview(self):
        """Get preview of sequence of angles to sample."""
        piline.preview_angles(self.piline)

    # %% ======= experimental sequence control functions =================

    def test_text(self):
        self.ui.outbox.append('txt changed')

    def test_val(self):
        self.ui.outbox.append('val changed')




    def run_seq(self):
        """Run an experimental sequence."""
        self.initialize_sequence()
        
        
        
        if self.seq_piline.isChecked():
            piline_angles = piline.get_angles(self.piline)
        
            for angle in piline_angles:
                
                self.ui.piline_set.setValue(float(angle)) 
                time.sleep(0.1)
                self.piline_set_now()
                
                time.sleep(2)
            
            
        
        
        '''
        
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
        '''
        self.finalize_sequence()

    def enable_during_seq(self, enabled):
        """Enable/disable GUI objects while a sequence is running."""
        items = [
            self.ui.run_seq, self.ui.set_seq_cycles,
            self.ui.pause_between_cycles, self.ui.seq_laser_trigger,
            self.ui.seq_polarizer_rot, self.ui.seq_raman_acquisition,
            self.ui.rotation_end, self.ui.rotation_start,
            self.ui.rotation_steps, self.ui.seq_mcl]
        [i.setEnabled(enabled) for i in items]
        
    def initialize_sequence(self):
        """Initialize settings when an experimental sequence starts."""
        self.export_settings()
        self.ui.abort_seq.setEnabled(True)
        self.enable_during_seq(False)
        self.ui.outbox.append('Sequence initiated')

    def finalize_sequence(self):
        """Finalize settings when an experimental sequence ends."""
        self.abort_seq = False
        self.ui.abort_seq.setEnabled(False)
        self.enable_during_seq(True)
        self.ui.outbox.append('Sequence complete.')

    def run_seq_thread(self):
        """Run sequence in a new thread."""
        worker = Worker(self.run_seq)  # pass other args here
        self.threadpool.start(worker)

    def abort_seq(self):
        """Abort the expreimental sequence."""
        self.ui.outbox.append('Sequence aborted after current cycle.')
        self.abort_seq = True


    # %% ============ Marzhauser MCL-3 stage controller ==================    


    def mcl_set_now_thread(self):
        """Set new stage position in a new thread."""
        worker = Worker(self.mcl_set_now)  # pass other args here
        self.threadpool.start(worker)

    def mcl_set_now(self):
        """Set the stage position."""
        mcl.set_now(self.mcl)

    def mcl_on_thread(self):
        """Open Marzhauser MCL-3 stage controller in a new thread."""
        worker = Worker(self.mcl_on)  # pass other args here
        self.threadpool.start(worker)

    def mcl_on(self):
        """Checkbox for MCL stage controller is checked/unchecked."""
        mcl.stage_on(self.mcl)
    
    def preview_grid_cords(self):
        """Preview the grid coordinates."""
        mcl.preview_grid_cords(self.mcl)


    # %% ========= Thorlabs KDC101 servo motor controllers= ==============

    def analyzer_on(self):
        """Checkbox for analyzer controller is checked/unchecked."""
        kcube.analyzer_on(self.kcube)

    def polarizer_on(self):
        """Checkbox for polarizer controller is checked/unchecked."""
        kcube.polarizer_on(self.kcube)

    def a_set_now_thread(self):
        """Move the analyzer to specified angle in a new thread."""
        worker = Worker(self.analyzer_set_now)  # pass other args here
        self.threadpool.start(worker)

    def analyzer_set_now(self):
        """Move the analizer to its home position."""
        kcube.analyzer_set_now(self.kcube)

    def p_set_now_thread(self):
        """Move the polarizer to specified angle in a new thread."""
        worker = Worker(self.polarizer_set_now)  # pass other args here
        self.threadpool.start(worker)

    def polarizer_set_now(self):
        """Move the polarizer to its home position."""
        kcube.polarizer_set_now(self.kcube)


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

    def avacs_on_thread(self):
        """Open connection to AVACS in a new thread."""
        worker = Worker(self.avacs_on)  # pass other args here
        self.threadpool.start(worker)

    def avacs_on(self):
        """Laseroptik beam attenuator checkbox is checked/unchecked."""
        avacs.avacs_on(self.avacs)
    
    def avacs_set_now_thread(self):
        """Set the AVACS beam attenuator angle in a new thread."""
        worker = Worker(self.avacs_set_now)  # pass other args here
        self.threadpool.start(worker)
    
    def avacs_set_now(self):
        """Set beam attenuator angle now."""
        avacs.set_now(self.avacs)

    # %% ============ system control functions =============================

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

    #def show_help():
    #    """Show the help window as an HTML popup."""
    #    ops.show_help()

    def quitapp(self):
        """Quit the application."""
        if self.srs['dev'] is not None:
            self.srs['dev'].close()
        if self.mso['dev'] is not None:
            self.mso['dev'].close()
        if self.avacs['dev'] is not None:
            self.avacs['dev'].close()
        if self.mcl['dev'] is not None:
            self.mcl['dev'].close()
        if self.piline['dev'] is not None:
            self.piline['dev'].close()
        # kill the process which opens LightField if its already running
        # os.system("taskkill /f /im AddInProcess.exe")
        # stop timer
        #self.timer.stop()
        # close app window
        self.deleteLater()
        self.close()
        # this kills the python kernel upon quitting
        sys.exit()

# %% ====================== run application ===============================

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    window = App()
    window.show()
    sys.exit(app.exec_())
