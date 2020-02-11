# Import the .NET class library
import clr

# Import python sys module
#import sys

# Import modules
import sys, os, glob#, string

from ctypes import *

# Import System.IO for saving and opening files
#from System.IO import *
import System.IO as sio


# Import c compatible List and String
from System import String
from System.Collections.Generic import List

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation


   
# Create the LightField Application (true for visible)
# The 2nd parameter forces LF to load with no experiment 
auto = Automation(False, List[String]())

# Get LightField Application object
application = auto.LightFieldApplication


# Get file manager object
file_manager = application.FileManager

# Open previously saved image or inform the user
# the file cannot be found
directory = 'C:\\Users\\a6q\\exp_data\\'



# Returns all .spe files
files = glob.glob(directory +'/*.spe')

# Returns recently acquired .spe file
last_image_acquired = max(files, key=os.path.getctime)


# Open file
file_name = file_manager.OpenFile(
    last_image_acquired, sio.FileAccess.Read)




# Access image
imageData = file_name.GetFrame(0, 0);

# Print Height and Width of first frame                
print(String.Format(
    '\t{0} {1}X{2}',
    "Image Width and Height:",
    imageData.Width,imageData.Height))

# Get image data
buffer = imageData.GetData()

# Print first 10 pixel intensities
for pixel in range(0,10):
    print(String.Format('\t{0} {1}', 'Pixel Intensity:',
                        str(buffer[pixel])))


# clear image buffer
file_name.Dispose()



