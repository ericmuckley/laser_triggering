
# Laser triggering


This respository contains code for an application which allows automated laser processing, including triggering of laser pulses, acquisition of Raman spectra, acquisition of traces from an oscilloscope, and motorized control of halfwave plates and polarizers.


## Use
The application is started by running the ```app.py``` file.

### Connecting to instruments

To view the avilable instrument ports, navigate to **Menu -> Show avilable instrument ports**. Addresses of each avilable VISA, serial, and FTID USB port will be printed in the output box. To connect with a particular instrument, navigate to the box for that instrument on the front panel of the GUI. Enter the appropriate address for the instrument in the **Address** field, and click the checkbox adjacent to the address field to connect to the instrument. For example: to communicate with the SRS DG645 pulse generator, enter the serial port address (e.g. COM6) in the address field and select the checkbox to connect to the device. The output box will indicate if connection to the instrument was successful. If the connection failed, check the instument address and connection to the PC. The user may also determine whether the instument can be identified by the PC using Windows Device Manager or National Instruments Measurement & Automation Explorer (NI MAX).

### Connecting to LightField
To acquire Raman spectra using Princeton Instruments LightField software, LightField must be opened from the GUI by clicking **Launch LightField**.' Once LightField loads, the user should load the LightField experiment called **Default Python Experiment**. After the experiment is loaded, settings can be modified in LightField. Raman spectra can be acquired by clicking the **Acquuire Raman spectrum*** button the the GUI.



### Running an experimental Sequence


   
        "Adjust the pulse "
        "width, pulse delay, pulse maplitude, and number of "
        "pulses in the edit boxes. Then click **Trigger pulses** to send pulses from the SRS. "
        "Uncheck the box to disconnect from the device."
        "\n=========================================================\n"
        
        "\n=========================================================\n"
        "To run the experimental sequence, check boxes for the "
        "pulse triggering and acquisition. Then click 'Run sequence'. "
        "Click 'Abort sequence' to stop the sequence prematurely."
        "\n=========================================================\n"



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
```conda create --name env --file requirements.txt```
where ```env``` is the name of the new environment.

After installation of the _thorlabs_apt_ library, three files in the support_files directory must be copied to the thorlabs_apt directory and placed in the same folder as _core.py_:
1. _APT.dll_
2. _ATP.lib_
3. _ATPAPI.h_

This allows communication between Thorlabs instruments, Windows, and Python.
