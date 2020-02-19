# -*- coding: utf-8 -*-
"""

Module to control the Thorlabs KCD101 K-Cube brushed motor controller

Created on Wed Feb 19 10:07:30 2020
@author: ericmuckley@gmail.com
"""


import time
import thorlabs_apt as apt


#filename = "%s/APT.dll" % os.path.dirname(__file__)



print(apt.list_available_devices())


dev = apt.Motor(27255762)


print(dev.hardware_info)

#print(dev.is_in_motion)

dev.set_velocity_parameters(0, 25, 25)

# max velocity and aceleration = 25.0

#motor.move_home(True)
#dev.move_to(45)
dev.move_by(5)



#print(os.path.dirname(__file__))

#print("%s/APT.dll" % os.path.dirname(__file__))

"""
FROM MANUAL:

// Set baud rate to 115200.
// 8 data bits, 1 stop bit, no parity
// RTS/CTS Handshake

"""



'''
dev = serial.Serial(port=srs['address'].text(), timeout=2)
dev.write('*IDN?\r'.encode())
srs['dev'] = dev
srs['outbox'].append('Pulse generator connected.')
srs['outbox'].append(dev.readline().decode("utf-8"))
enable_pulse_gen_buttons(srs, True)
except serial.SerialException:
srs['outbox'].append('Pulse generator could not connect.')
srs['on'].setChecked(False)
enable_pulse_gen_buttons(srs, False)
srs['dev'] = None
if not srs['on'].isChecked():
try:
srs['dev'].close()
except AttributeError:
pass
srs['dev'] = None
srs['outbox'].append('Pulse generator closed.')
srs['on'].setChecked(False)
enable_pulse_gen_buttons(srs, False)
'''


if __name__ == '__main__':
    pass