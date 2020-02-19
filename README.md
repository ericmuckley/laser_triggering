
# Laser triggering


## **This repo is currently under construction**


This respository contains code for an application which allows automated laser processing, including triggering of laser pulses, acquisition of Raman spectra, acquisition of traces from an oscilloscope, and motorized control of halfwave plates and polarizers.



## Use
The application is started by running the ```app.py``` file.


## Description of files

* **Main repository**
    * **app.py**: main file for starting the GUI application. Calls _ui.ui_ and files inside _instr_files_ directory to create the application.
    * **README.md**: the file you are reading, which describes instructuins for use
    * **ui.ui**: user interface file, created in QT Desginer, which is called by _app.py_ and provides thelayout of graphical user interface widgets for the application.
    * **RUN_LASER_TRIGGERING.bat**: Windows bat file. Make a shortcut of this file and place it anywhere on the PC to run _app.py_ by clicking on the shortcut.
    * **requirements.txt**: text file containing list of all dependencies. These can be installed using Anaconda as described in the _Installation_ section below.
* **instr_libs**
    * **avacs.py**: modules for controlling Laseroptik AVACS beam attenuator
    * **kcube.py**: modules for controlling Thorlabs KDC101 brushed servo motor controllers
    * **lf.py**: modules for controlling Princeton Instruments LightField software
    * **mso.py**: modules for controlling Tektronix MSO64 oscilloscope
    * **ops.py**: modules for controlling operations and file I/O of the main GUI
    * **srs.py**: modules for controlling SRS DG645 digital delay pulse generator
* **logs**: default directory for saving experiment configuration files and logging experimental data
* **support_files**: directory for storing supporting files (_APT.dll_, _APTAPI.h_, _ATP.lib_) and other unused depreciated files





## Installation of dependencies
Prior to use, Python libraries and dependencies must be installed. To install dependencies, it is recommended to use Anaconda (https://www.anaconda.com/distribution/#download-section).

To install all dependencies on a Windows 64-bit computer, create an Anaconda envinrment and populate it with the required dependencies by opening the Anaconda command prompt and running: 
```conda create --name <env> --file requirements.txt```
where <env> is the name of the new environment.

After installation of the _thorlabs_apt_ library, three files in the support_files directory must be copied to the thorlabs_apt directory and placed in the same folder as _core.py_:
1. _APT.dll_
2. _ATP.lib_
3. _ATPAPI.h_

This allows communication between Thorlabs instruments, Windows, and Python.
