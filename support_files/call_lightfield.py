
import os
import sys


# --------------------- for LightField dependencies ------------------------
import clr  # the .NET class library
import System.IO as sio# import *  # for saving and opening files
# Import c compatible List and String
from System import String
from System.Collections.Generic import List

# Add needed dll references for LightField
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')
# Princeton Instruments imports
from PrincetonInstruments.LightField.Automation import Automation



def add_available_devices():
    # Add first available device and return
    for device in sio.experiment.AvailableDevices:
        print("\n\tAdding Device...")
        sio.experimentexperiment.Add(device)
        return device

# create a C# compatible List of type String object
list1 = List[String]()

# add the command line option for an empty experiment
list1.Add("/empty")

# Create the LightField Application (true for visible)
auto = Automation(True, List[String](list1))







