# -*- coding: utf-8 -*-

"""
GUI applicaton for controlling laser pulses using an SRS DG645 digital
delay pulse generator.

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
#from shapely.geometry import LineString


'''
# --------------------- for LightField dependencies ------------------------
import clr  # the .NET class library
#import System.IO as sio  # for saving and opening files
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
    
'''





# change matplotlib settings to make plots look nicer
'''
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
    Ui_MainWindow, QtBaseClass = uic.loadUiType('UI.ui')

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
        self.ui.run_seq.clicked.connect(self.run_seq_thread)
        self.ui.abort_seq.clicked.connect(self.abort_seq)
        #self.ui.launch_lf.clicked.connect(self.launch_lf_thread)
        
        # assign actions to checkboxes
        # example: self.ui.CHECKBOX.stateChanged.connect(self.FUNCTION_NAME)
        self.ui.pulsegen_on.stateChanged.connect(self.pulsegen_on)
        
        # set default data folder and create it if it doesn't exist
        #self.filedir = os.getcwd()+'\\QCMD_model_results'
        #if not os.path.exists(self.filedir):
        #    os.makedirs(self.filedir)

        self.srs = {'dev': None}
        self.lf = {'app': None}

    
    
    

    # %% ========= Princeton Instruments LightField control ==============
    '''


    def add_available_devices(self):
        # Add first available device and return
        for device in sio.experiment.AvailableDevices:
            print("\n\tAdding Device...")
            sio.experimentexperiment.Add(device)
            return device


    def launch_lf_thread(self):
        """Launch LightField software in a new thread."""
        worker = Worker(self.launch_lf)  # pass other args here
        self.threadpool.start(worker)


    def launch_lf(self):
        """Launch LightField software."""
        # create a C# compatible List of type String object
        list1 = List[String]()
        # add the command line option for an empty experiment
        list1.Add("/empty")
        # create the LightField Application (true for visible)
        self.lf['app'] = Automation(True, List[String](list1))
    

    '''


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
            except serial.SerialException:
                self.ui.outbox.append('Pulse generator could not connect.')
                self.ui.config_pulse_frame.setEnabled(False)
                self.ui.pulsegen_address.setEnabled(True)
                self.ui.pulsegen_on.setChecked(False)
                self.srs['dev'] = None
        else: 
            try:
                self.srs['dev'].close()
            except AttributeError:
                pass
            self.srs['dev'] = None
            self.ui.outbox.append('Pulse generator closed.')
            self.ui.pulsegen_on.setChecked(False)

        
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
        for i in range(10):
            self.ui.outbox.append('testing...{}'.format(i))
            time.sleep(1)
            if self.abort_seq == True:
                break
        self.abort_seq = False
        self.ui.run_seq.setEnabled(True)
        self.ui.abort_seq.setEnabled(False)

    def run_seq_thread(self):
        """Run sequence in a new thread."""
        worker = Worker(self.run_seq)  # pass other args here
        self.threadpool.start(worker)




    # %% ============ system control functions =============================

    def show_help(self):
        """Print help in the GUI output box."""
        help_message = (
            "\n===================\n"
            "HELP"
            "\n===================\n"
            "To determine which serial ports are avilable for "
            "connected instruments, click "
            "'Menu --> Show available serial ports'."
            "\n===================\n"
            "To communicate with the SRS DG645 pulse generator, "
            "enter the serial port address (e.g. COM6) in the address "
            "field and ckeck the checkbox to connect to the device. "
            "Adjust the pulse "
            "width, pulse delay, pulse maplitude, and number of "
            "pulses in the edit boxes. Then click 'Trigger pulses' "
            "to send pulses from the SRS. "
            "Uncheck the box to disconnect from the device."
            "\n===================\n"
            "To run the experimental sequence, click 'Run sequence' and "
            "'Abort sequence' to stop the sequence. "
            )
        self.ui.outbox.append(help_message)
        


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


    def mu_eta_mesh(self, uidict):
        """Create mesh of mu and eta valuses using inputs on UI."""
        # get 2D 1mesh grid points of log mu and eta values
        step_num=50
        mu_mesh, eta_mesh = np.meshgrid(
                np.linspace(uidict['mu_low'], uidict['mu_high'],
                            step_num).astype(float),
                np.linspace(uidict['eta_low'], uidict['eta_high'],
                            step_num).astype(float))
        #get mesh of mu and eta values and corresponding DF and DD values        
        df_surf, dd_surf = self.kelvin_voigt(
                             10**mu_mesh,
                             10**eta_mesh,
                             rho_f=uidict['rho'],
                             h_f=uidict['h'],
                             n=uidict['n'],
                             f0=uidict['f0'],
                             medium=uidict['medium'])
        return mu_mesh, eta_mesh, df_surf, dd_surf          


    def fit_model(self):
        """Run modeling of the QCM-D dtaa using inputs from UI. """
        self.ui.fit_model.setDisabled(True)
        self.ui.outbox.append('------------------------------------------')
        self.ui.outbox.append('Fitting model...')
        # get dictionary of input values from UI
        uidict = self.get_ui_inputs()
        self.results = uidict.copy()
        self.contours = {}
        
        # get grid of possible mu, eta, df, and dd values
        mu_mesh, eta_mesh, df_surf, dd_surf = self.mu_eta_mesh(uidict)
        # plot delta F heatmap
        plt.ioff()
        df_cont_plot = plt.contour(
                mu_mesh, eta_mesh, df_surf, uidict['df_exp'])
        # plot delta D heatmap
        dd_cont_plot = plt.contour(
                mu_mesh, eta_mesh, dd_surf, uidict['dd_exp'])
        
        # extract contours which correspond to experimental values
        df_cont = self.get_contour(df_cont_plot)
        dd_cont = self.get_contour(dd_cont_plot)
        # find intersection of solutions
        intersection_list = np.array(
                self.find_intersections(df_cont, dd_cont))
        plt.cla()
        # if there are any solutions, select the 0th-order solution
        if len(intersection_list) > 0:
            sol = sorted(intersection_list, key = lambda i: float(i[1]))[-1]
            
            # get calculated mu and eta values, along with G' and G'' 
            mu, eta, = 10**sol[0], 10**sol[1]
            Gp, Gdp = mu, 2*np.pi*uidict['f0']*eta
            # get fitted df and dd values
            df_fit, dd_fit = self.kelvin_voigt(mu, eta,
                                               rho_f=uidict['rho'],
                                               h_f=uidict['h'],
                                               n=uidict['n'],
                                               f0=uidict['f0'],
                                               medium=uidict['medium'])
            # get penetration depth
            pen_dep = self.get_penetration_depth(uidict['f0'], eta,
                                                 uidict['rho'])
            
            self.results.update({'df_fit': df_fit, 'dd_fit': dd_fit,
                                 'mu': mu, 'eta': eta,
                                 'penetration_depth': pen_dep,
                                 "G'": Gp, "G''": Gdp})
            self.contours.update({'df_exp': uidict['df_exp'],
                                  'dd_exp': uidict['dd_exp'],
                                  'mu_mesh': mu_mesh, 'eta_mesh': eta_mesh,
                                  'df_surf': df_surf, 'dd_surf': dd_surf,
                                  'df_cont': df_cont, 'dd_cont': dd_cont,
                                  'sol': sol})

            self.ui.outbox.append(
                    'Found '+str(len(intersection_list))+' solutions.')
            self.ui.outbox.append('First-order solution:')
            self.ui.plot_sol_surf.setDisabled(False)
            self.ui.plot_df_surf.setDisabled(False)
            self.ui.plot_dd_surf.setDisabled(False)
            self.ui.export_results.setDisabled(False)
            for key in self.results:
                self.ui.outbox.append(str(key)+': '+str(self.results[key]))

        else:
            self.ui.outbox.append(
                    '\n\nNo solutions exist with these parameters.')
            self.ui.plot_sol_surf.setDisabled(True)
            self.ui.plot_df_surf.setDisabled(True)
            self.ui.plot_dd_surf.setDisabled(True)
            self.ui.export_results.setDisabled(True)
        self.ui.fit_model.setDisabled(False)
        self.ui.outbox.moveCursor(QtGui.QTextCursor.End)


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


    def plot_dd_surf(self):
        """Plot delta D surface."""
        plt.cla()
        fig_dd = plt.figure(2)
        plt.ion()
        plt.contour(self.contours['mu_mesh'], self.contours['eta_mesh'],
                    self.contours['dd_surf'], self.contours['dd_exp'])
        plt.contourf(self.contours['mu_mesh'], self.contours['eta_mesh'],
                     self.contours['dd_surf'], 50, cmap='rainbow')
        self.plot_setup(title='ΔD (x 10^-6)',
                   labels=['Log (μ) (Pa)', 'Log (η) (Pa s)'], colorbar=True)
        plt.tight_layout()
        fig_dd.canvas.set_window_title('ΔD surface')
        fig_dd.show()


    def plot_sol_surf(self):
        """Plot solution surface."""
        plt.cla()
        fig_df = plt.figure(3)
        plt.ion()
        plt.scatter(self.contours['sol'][0],
                    self.contours['sol'][1], marker='x',
                    s=300, c='k', label='solution')
        # plot contour intersection
        plt.scatter(self.contours['df_cont'][:, 0],
                    self.contours['df_cont'][:, 1], s=1, c='b', label='df')
        plt.scatter(self.contours['dd_cont'][:, 0],
                    self.contours['dd_cont'][:, 1], s=1, c='r', label='dd')
        self.plot_setup(title='Solution',
                   labels=['Log (μ) (Pa)', 'Log (η) (Pa s)'], legend=True)
        plt.tight_layout()
        fig_df.canvas.set_window_title('Solution')
        fig_df.show()


    def plot_setup(self, labels=['X', 'Y'], fsize=20, setlimits=False,
                   title=None, legend=False, colorbar=False,
                   limits=[0,1,0,1], save=False, filename='plot.jpg'):
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


    def kelvin_voigt(self, mu_f, eta_f, rho_f=1e3, h_f=1e-6, n=1, f0=5e6,
                    medium='air'):
        """ 
        The Kelvin-Voigt model comes from eqns (15) in the paper by 
        Voinova: Vionova, M.V., Rodahl, M., Jonson, M. and Kasemo, B., 1999.
        Viscoelastic acoustic response of layered polymer films at fluid-solid
        interfaces: continuum mechanics approach. Physica Scripta, 59(5), p.391.
        Reference: https://github.com/88tpm/QCMD/blob/master
        /Mass-specific%20activity/Internal%20functions/voigt_rel.m.
        
        This function solves for Delta f and Delta d of thin adlayer on QCM.
        It differs from voigt because it calculates relative to an
        unloaded resonator.
        Inputs
            mu_f = shear modulus of film in Pa
            eta_f = shear viscosity of film in Pa s
            rho_f = density of film in kg m-3
            h_f = thickness of film in m
            n = crystal harmonic number
            f0 = fundamental resonant frequency of crystal in Hz      
        Output
            deltaf = frequency change of resonator
            deltad =  dissipation change of resonator
        """
        # define properties of QCM crystal
        w = 2*np.pi*f0*n  # angular frequency
        mu_q = 2.947e10  # shear modulus of AT-cut quatz in Pa
        rho_q = 2648  # density of quartz (kg/m^3)
        h_q = np.sqrt(mu_q/rho_q)/(2*f0)  # thickness of quartz
        # define properties of medium
        if medium == 'air':
            rho_b = 1.1839  # density of bulk air (25 C) in kg/m^3
            eta_b = 18.6e-6  # viscosity of bulk air (25 C) in Pa s
        if medium == 'water':
            rho_b = 1000  # density of bulk water in kg/m^3
            eta_b = 8.9e-4  # viscosity of bulk water in Pa s
        # define equations from the Kelvin-Voigt model in publication
        # eqn 14
        kappa_f = eta_f-(1j*mu_f/w)
        # eqn 13
        x_f = np.sqrt(-rho_f*np.square(w)/(mu_f + 1j*w*eta_f))
        x_b = np.sqrt(1j*rho_b*w/eta_b)
        # eqn 11 after simplification with h1 = h2 and h3 = infinity
        A = (kappa_f*x_f+eta_b*x_b)/(kappa_f*x_f-eta_b*x_b)
        # eqn 16
        beta = kappa_f*x_f*(1-A*np.exp(2*x_f*h_f))/(1+A*np.exp(2*x_f*h_f))
        beta0 = kappa_f*x_f*(1-A)/(1+A)
        # eqn 15
        df = np.imag((beta-beta0)/(2*np.pi*rho_q*h_q))
        dd = -np.real((beta-beta0)/(np.pi*f0*n*rho_q*h_q))*1e6
        return df, dd


    def get_contour(self, cont_plot):
        """Get ordered pairs of contour lines from a contour plot.
        Input should be defined as:
        cont_plot = plt.contour(x_mesh, y_mesh, z_surf, contour_value)"""
        # extract contour paths from plot
        paths = [path.vertices for path in cont_plot.collections[0].get_paths()]
        if paths:
            # stack all contour paths in a single 2D array
            return np.vstack(paths)
        else:
            return []


    def find_intersections(self, op_list1, op_list2):
        """Find all intersections between two curves. Curves are defined by lists
        of ordered pairs (x, y).
        Returns an empty list if no intersections are found."""
        intersections = []
        # check if both curves contain more than 1 point:
        if len(op_list1) > 1 and len(op_list2) > 1:
            # loop over each pair of line segments
            for i1 in range(len(op_list1)-1):
                for i2 in range(len(op_list2)-1):
                    # create segment from the first set of points
                    seg1 = LineString([(op_list1[i1][0], op_list1[i1][1]),
                                    (op_list1[i1+1][0], op_list1[i1+1][1])])
                    # create segment from the second set of points
                    seg2 = LineString([(op_list2[i2][0], op_list2[i2][1]),
                                    (op_list2[i2+1][0], op_list2[i2+1][1])])
                    # check if segment from set-1 intersects segment from set-2
                    if seg1.intersects(seg2):
                        avg_x = np.mean([op_list1[i1][0], op_list1[i1+1][0],
                                        op_list2[i2][0], op_list2[i2+1][0]])
                        avg_y = np.mean([op_list1[i1][1], op_list1[i1+1][1],
                                        op_list2[i2][1], op_list2[i2+1][1]])
                        intersections.append([avg_x, avg_y])
        return intersections


    def get_penetration_depth(self, freq, eta, rho):
        """Calculate penetration depth of acoustic wave using the QCM
        resonant requency (freq), adlayer visacosity (eta), and adlayer
        density (rho)."""
        return np.sqrt(eta / (np.pi * freq * rho))


    def quitapp(self):
        """Quit the application."""
        self.deleteLater()
        # self.timer.stop()  # stop timer
        # close app window
        self.close()  
        # kill python kernel
        sys.exit()  

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