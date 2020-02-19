
# Laser triggering


## **This repo is currently under construction**


This respository contains code for an application which allows automated laser processing, including triggering of laser pulses, acquisition of Raman spectra, acquisition of traces from an oscilloscope, and motorized control of halfwave plates and polarizers.



## Use
The application is started by running the ```app.py``` file.



## Installation of dependencies
Prior to use, Python libraries and dependencies must be installed. To install dependencies, it is recommended to use Anaconda (https://www.anaconda.com/distribution/#download-section).

After installation of the _thorlabs_apt_ library, three files in the support_files directory must be copied to the thorlabs_apt directory and placed in the same folder as _core.py_:
1. _APT.dll_
2. _ATP.lib_
3. _ATPAPI.h_
