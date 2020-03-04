#!/usr/bin python
# -*- coding: utf-8 -*-

"""

To execute the sample application,
the following files must be installed:

- PI_GCS2_DLL.dll


Proceed as follows to make these
 files available for the application:
Install the feature "PI_GCS_Library_PI_GCS2_DLL_Setup.exe" 
rom the product CD.




(c)2015-2017 Physik Instrumente (PI) GmbH & Co. KG
Software products that are provided by PI are subject to the General Software License Agreement of Physik Instrumente (PI) GmbH & Co. KG and may incorporate and/or make use of third-party software components. For more information, please read the General Software License Agreement and the Third Party Software Note linked below.
General Software License Agreement :
http://www.physikinstrumente.com/download/EULA_PhysikInstrumenteGmbH_Co_KG.pdf
Third Party Software Note :
http://www.physikinstrumente.com/download/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf
"""

"""This example shows how to realize a cyclic circular motion with trajectories."""


import numpy as np
from pipython import GCSDevice, pitools
from pipython.datarectools import getservotime

CONTROLLERNAME = 'C-867.2U2'
STAGES = ('U-521.24', 'U-521.24')  # connect stages to axes
REFMODE = ('FRF', 'FRF')  # reference the connected stages

PERIOD = 5.0  # duration of one sine period in seconds as float
CENTERPOS = (1.0, 1.0)  # center position of the circular motion as float for both axes
AMPLITUDE = (1.0, 1.0)  # amplitude (i.e. diameter) of the circular motion as float for both axes
BUFFERMIN = 10  # minimum number of points in buffer until motion is started


def main():
    """Connect controller, setup stages and start trajectories."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.ConnectRS232(comport=24, baudrate=115200)
        # pidevice.ConnectUSB(serialnum='123456789')
        # pidevice.ConnectTCPIP(ipaddress='192.168.178.42')
        print('connected: {}'.format(pidevice.qIDN().strip()))
        print('maximum buffer size: {}'.format(
                pidevice.qSPA(1, 0x22000020)[1][0x22000020]))
        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmode=REFMODE)
        runprofile(pidevice)


def runprofile(pidevice):
    """Move to start position, set up and run trajectories and wait
    until they are finished.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    # this sample requires two connected axes
    assert 2 == len(pidevice.axes[:2])
    trajectories = (1, 2)
    # maximum buffer size
    numpoints = pidevice.qSPA(1, 0x22000020)[1][0x22000020]  
    xvals = [2*np.pi*float(i) / float(numpoints) for i in range(numpoints)]
    xtrajectory = [CENTERPOS[0]+AMPLITUDE[0]/2.0*np.sin(xval) for xval in xvals]
    ytrajectory = [CENTERPOS[1]+AMPLITUDE[1]/2.0*np.cos(xval) for xval in xvals]
    print('move axes {} to their start positions {}'.format(
            pidevice.axes[:2], (xtrajectory[0], ytrajectory[0])))
    pidevice.MOV(pidevice.axes[:2], (xtrajectory[0], ytrajectory[0]))
    pitools.waitontarget(pidevice, pidevice.axes[:2])
    servotime = getservotime(pidevice)
    tgtvalue = int(float(PERIOD) / float(numpoints) / servotime)
    print('set %d servo cycles per point -> period of %.2f seconds' % (
            tgtvalue, tgtvalue * servotime * numpoints))
    pidevice.TGT(tgtvalue)
    print('trajectory timing: {}'.format(pidevice.qTGT()))
    print('clear existing trajectories')
    pidevice.TGC(trajectories)
    pointnum = 0
    print('\r%s' % (' ' * 40)),
    while pointnum < numpoints:
        if pidevice.qTGL(1)[1] < BUFFERMIN:
            pidevice.TGA(trajectories,
                         (xtrajectory[pointnum], ytrajectory[pointnum]))
            pointnum += 1
            print('\rappend point {}/{}'.format(pointnum, numpoints)),
        if BUFFERMIN == pointnum:
            print('\nstarting trajectories')
            pidevice.TGS(trajectories)
        if numpoints == pointnum:
            print('\nfinishing trajectories')
            pidevice.TGF(trajectories)
    pitools.waitontrajectory(pidevice, trajectories)
    print('done')


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
