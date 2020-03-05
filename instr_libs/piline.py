# -*- coding: utf-8 -*-

"""
This module contains methods for controlling the PI C-867 PILine
roation controller. The PI_GCS2_DLL.dll library must be installed
for this script to run.
Install using "PI_GCS_Library_PI_GCS2_DLL_Setup.exe".

Parts of this script were written by PI:
(c)2015-2017 Physik Instrumente (PI) GmbH & Co. KG
Software products that are provided by PI are subject to the
General Software License Agreement of Physik Instrumente (PI)
GmbH & Co. KG and may incorporate and/or make use of third-party
software components. For more information, please read the General
Software License Agreement and the Third Party Software Note
linked below.
General Software License Agreement :
http://www.physikinstrumente.com/download/EULA_PhysikInstrumenteGmbH_Co_KG.pdf
Third Party Software Note :
http://www.physikinstrumente.com/download/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf


DIP switches on the back of the PI C-867 unit should be set before
powering the unit so that the controller "Address = 1":
    1 - 4: ON
    5 - 8: OFF

Created on Wed Mar  4 11:38:43 2020
@author: ericmuckley@gmail.com
"""

#import time
#import numpy as np
#from pipython import GCSDevice, pitools, GCSError, gcserror
#from pipython.datarectools import getservotime

import time
import serial



def print_ports():
    """Print a list of avilable serial ports."""
    ports = list(serial.tools.list_ports.comports())
    print('Available serial ports:')
    [print(p.device) for p in ports]

def get_id(dev):
    """Get ID of device."""
    dev.write(('*IDN?\n').encode())
    return dev.readline().decode()

def get_position(dev):
    """Get current real position."""
    dev.write(('POS?\n').encode())
    return dev.readline().decode()   

def get_stage_type(dev):
    """Get the stage type connected to the controller."""
    dev.write(('CST?\n').encode())
    return dev.readline().decode() 

def get_servo_mode(dev):
    """Get servomotor mode."""
    dev.write(('SVO?\n').encode())
    return bool(int(dev.readline().decode().split('=')[1]))

def turn_on_servo(dev, on=True):
    """Turn on or off the servo motor."""
    dev.write(('SVO 1 '+str(int(on))+'\n').encode())

def get_motion_lims(dev):
    """Get min and max motion limits of the stage."""
    dev.write(('TMN?\n').encode())
    min_lim = dev.readline().decode().split('=')[1]
    dev.write(('TMX?\n').encode())
    max_lim = dev.readline().decode().split('=')[1]
    dev.write(('LIM?\n').encode())
    lim_switches = dev.readline().decode().split('=')[1]
    return (min_lim, max_lim, lim_switches)

def check_servo(dev):
    """Check whether servo motor is on."""
    dev.write(('SVO?\n').encode())
    return bool(int(dev.readline().decode().split('=')[1]))

def get_error(dev):
    """Return error of the device.""" 
    dev.write(('ERR?\n').encode())
    return dev.readline().decode()

def get_reference_mode(dev):
    """Get reference mode of the device."""
    dev.write(('RON?\n').encode())
    return dev.readline().decode()

def get_reference_result(dev):
    """Get result of reference query."""
    dev.write(('FRF? 1\n').encode())
    return dev.readline().decode()

def initialize_stage(dev):
    """Initialize the stage and get some operating parameters."""
    turn_on_servo(dev, on=True)
    # read stage information
    print('Controller ID: {}'.format(get_id(dev)))
    print('stage type: {}'.format(get_stage_type(dev)))
    print('current position: {}'.format(get_position(dev)))
    print('servo on: {}'.format(check_servo(dev)))
    print('reference mode: {}'.format(get_reference_mode(dev)))
    # get reference point and wait until its finished
    dev.write(('FRF 1\n').encode())
    time.sleep(6)
    ref_result = bool(int(get_reference_result(dev).split('=')[1]))
    print('Reference successful: {}'.format(ref_result))
    print('Stage configured successfully.')


if __name__ == '__main__':


    address = 'COM24'
    dev = serial.Serial(port=address, baudrate=115200, timeout=2)
    initialize_stage(dev)
    #time.sleep(pause)
 
    #dev.write(('FED 1\n').encode())
    #print('result: {}'.format(dev.readline().decode()))

    #dev.write(('GOH\n').encode())
    
    #dev.write(('POS 1 0\n').encode())
    
    #dev.write(('MVR 1 0\n').encode())

    dev.write(('MOV 1 360\n').encode())

    time.sleep(5)

    #dev.write(('MVR 1 10\n').encode())
    #dev.write(('TRS?\n').encode())
    #print('result: {}'.format(dev.readline().decode()))


    
    turn_on_servo(dev, on=False)

    print('current position: {}'.format(get_position(dev)))

    print('error code: {}'.format(get_error(dev)))
    dev.close()



# set name of controller and stages
#CONTROLLERNAME = 
'''
PERIOD = 5.0  # duration of one sine period in seconds as float
CENTERPOS = (1.0, 1.0)  # center position of the circular motion as float for both axes
AMPLITUDE = (1.0, 1.0)  # amplitude (i.e. diameter) of the circular motion as float for both axes
BUFFERMIN = 10  # minimum number of points in buffer until motion is started


def getaxeslist(pidevice, axes):
    """Return list of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list of them or None for all axes.
    @return : List of axes from 'axes' or all axes or empty list.
    """
    axes = pidevice.axes if axes is None else axes
    if not axes:
        return []
    if not hasattr(axes, '__iter__'):
        axes = [axes]
    return axes


def waitonready(pidevice, timeout=60, predelay=0, polldelay=0.1):
    """Wait until controller is on "ready" state and finally query controller error.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    time.sleep(predelay)
    if not pidevice.HasIsControllerReady():
        return
    maxtime = time.time() + timeout
    while not pidevice.IsControllerReady():
        if time.time() > maxtime:
            raise SystemError('waitonready() timed out after %.1f seconds' % timeout)
        time.sleep(polldelay)
    pidevice.checkerror()




# Too many arguments (6/5) pylint: disable=R0913
def waitontarget(pidevice, axes=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list, or None to wait for all axes.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitonready(pidevice, timeout, predelay)
    maxtime = time.time() + timeout
    while not all(list(pidevice.qONT(axes).values())):
        if time.time() > maxtime:
            raise SystemError('waitontarget() timed out after %.1f seconds' % timeout)
        time.sleep(polldelay)
    time.sleep(postdelay)


def stopall(pidevice):
    """Stop motion of all axes and mask the "error 10" warning.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    try:
        pidevice.StopAll()
    except GCSError as exc:
        if gcserror.E10_PI_CNTR_STOP != exc:  # error 10 is just a warning that the device has been stopped
            raise



def startup(pidevice, stages=None, refmode=None):
    """Define 'stages', stop all, enable servo on all connected axes and reference them with 'refmode'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param stages : Name of stages to initialize as string or list or None to skip.
    @param refmode : Name of referencing commands as string or list or None to skip.
    If list then one entry for each axis, None to skip an axis. If it is a single string
    all axes will be referenced with this command.
    """
    if stages:
        allaxes = pidevice.qSAI_ALL()
        stages = stages if isinstance(stages, (list, tuple)) else [stages]
        stages = stages[:len(allaxes)]
        allaxes = allaxes[:len(stages)]
        pidevice.CST(allaxes, stages)
    if pidevice.HasINI():
        pidevice.INI()
    if pidevice.HasONL():
        pidevice.ONL(list(range(1, pidevice.numaxes + 1)), [True] * pidevice.numaxes)
    stopall(pidevice)
    pidevice.SVO(pidevice.axes, [True] * len(pidevice.axes))
    waitontarget(pidevice, axes=pidevice.axes)
    referencedaxes = []
    if refmode:
        refmode = refmode if isinstance(refmode, (list, tuple)) else [refmode] * pidevice.numaxes
        refmode = refmode[:pidevice.numaxes]
        reftypes = set(refmode)
        for reftype in reftypes:
            if reftype is None:
                continue
            axes = [pidevice.axes[i] for i in range(len(refmode)) if refmode[i] == reftype]
            getattr(pidevice, reftype.upper())(axes)
            referencedaxes += axes
    waitontarget(pidevice, axes=referencedaxes)


def main():
    """Connect controller, setup stages and start trajectories."""
    with GCSDevice('C-867.2U2') as pidevice:
        pidevice.ConnectRS232(comport=24, baudrate=115200)
        # pidevice.ConnectUSB(serialnum='123456789')
        # pidevice.ConnectTCPIP(ipaddress='192.168.178.42')
        print('connected: {}'.format(pidevice.qIDN().strip()))
        #print('maximum buffer size: {}'.format(
        #        pidevice.qSPA(1, 0x22000020)[1][0x22000020]))
        print('initialize connected stages...')
        startup(pidevice, stages=('U-521.24', 'U-521.24'), refmode=('FRF', 'FRF'))
        print('startup complete.')
        #runprofile(pidevice)


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
    waitontarget(pidevice, pidevice.axes[:2])
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
'''