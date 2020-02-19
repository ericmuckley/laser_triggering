
# Laser triggering


## **This repo is currently under construction**


This respository contains code for an application which allows automated laser processing, including triggering of laser pulses, acquisition of Raman spectra, acquisition of traces from an oscilloscope, and motorized control of halfwave plates and polarizers.



## Use
The application is started by running the ```app.py``` file.


## Description of files

* Main repository
    * _app.py_
        * main file for starting the GUI application
    * _README.md_
        * this file, which describes instructuins for use
    * _ui.ui_
        * user interface file, created in QT Desginer, which is called by _app.py_ and provides thelayout of graphical user interface widgets for the application.
    * RUN_LASER_TRIGGERING.bat_: Windows bat file. Make a shortbut of this file and place anywhere on the PC to run _app.py_ by clicking on the shortcut.
* instru_libs
    * _avacs.py_:
    * _kcube.py_:



## Installation of dependencies
Prior to use, Python libraries and dependencies must be installed. To install dependencies, it is recommended to use Anaconda (https://www.anaconda.com/distribution/#download-section).

After installation of the _thorlabs_apt_ library, three files in the support_files directory must be copied to the thorlabs_apt directory and placed in the same folder as _core.py_:
1. _APT.dll_
2. _ATP.lib_
3. _ATPAPI.h_

This allows communication between Thorlabs instruments, Windows, and Python.
