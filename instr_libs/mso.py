# -*- coding: utf-8 -*-
"""

Modules for controlling Tektronix MSO64 oscilloscope.

Created on Mon Feb 17 16:27:52 2020
@author: ericmuckley@gmail.com
"""

import visa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time



def enable_mso(mso, enabled):
    """Enable/disable GUI objects realted to the oscilloscope."""
    items = ['acquire',  'downsample', 'export_scope_trace']
    [mso[i].setEnabled(enabled) for i in items]
    mso['address'].setEnabled(not enabled)


def mso_on(mso):
    "Run this function when MSO64 oscilloscope checkbox is checked."""
    if mso['on'].isChecked():
        try:
            rm = visa.ResourceManager()
            dev = rm.open_resource(mso['address'].text())
            mso['dev'] = dev
            mso['outbox'].append('Oscilloscope connected.')
            mso['outbox'].append(dev.query('*IDN?'))
            enable_mso(mso, True)
        except:
            mso['outbox'].append('Oscilloscope could not connect.')
            enable_mso(mso, True)
            mso['dev'] = None
            mso['on'].setChecked(False)
    if not mso['on'].isChecked():
        try:
            mso['dev'].close()
        except AttributeError:
            pass
        mso['dev'] = None
        mso['outbox'].append('Oscilloscope closed.')
        mso['on'].setChecked(False)
        enable_mso(mso, True)




def get_scope_timescale(mso, signal, downsample=10):
    """Get the time-scale associated with the scope signal."""
    # get time-scale increment
    dt = float(mso['dev'].query('WFMOutpre:XINcr?'))
    # calculate the actual values of the x-scale
    t_scale = np.linspace(0, len(signal)*downsample*dt,
                          num=int(len(signal)))
    return t_scale


def acquire(mso):
    """Acquire and plot signal on oscilloscope."""
    mso['dev'].write(':DATA:SOURCE CH1')
    mso['dev'].write(':DATa:START 1')
    mso['dev'].write(':DATa:STOP 12500000')
    mso['dev'].write(':WFMOutpre:ENCDG ASCII')
    mso['dev'].write(':WFMOOutpre:BYT_NR 1')
    downsample = mso['downsample'].value()
    # get signal from scope
    signal_raw = np.array(mso['dev'].query(':CURVE?').split(','))
    signal = signal_raw.astype(float)[::downsample]
    # get timescale associated with scope trace        
    timescale = get_scope_timescale(mso, signal, downsample=downsample)
    # plot scope trace
    plt.ion()
    fig = plt.figure(1)
    fig.clf()
    plt.plot(timescale, signal, lw=1)
    plot_setup(labels=('Time (s)', 'Signal'), legend=False)
    fig.canvas.set_window_title('Oscilloscope trace')
    plt.draw()
    mso['outbox'].append('Oscilloscope trace acquired.')
    mso['last_sig'] = np.column_stack((timescale, signal))
    mso['last_sig_ts'] = time.strftime('%Y-%m-%d_%H-%M-%S')
    mso['export'].setEnabled(True)


def export_scope_trace(mso):
    """Export most recent oscilloscope trace to file."""
    df = pd.DataFrame(data=mso['last_sig'],
                      columns=['time', 'signal'])
    path = mso['logdir']+'\\'+mso['last_sig_ts']+'__scope_trace.csv'
    df.to_csv(path, index=False)
    mso['outbox'].append('Oscilloscope trace exported.')
    
    
    
def plot_setup(labels=['X', 'Y'], fsize=20, setlimits=False,
               title=None, legend=True, limits=(0,1,0,1)):
    """Creates a custom plot configuration to make graphs look nice.
    This can be called with matplotlib for setting axes labels,
    titles, axes ranges, and the font size of plot labels.
    This should be called between plt.plot() and plt.show() commands."""
    plt.xlabel(str(labels[0]), fontsize=fsize)
    plt.ylabel(str(labels[1]), fontsize=fsize)
    #fig = plt.gcf()
    #fig.set_size_inches(6, 4)
    if title:
        plt.title(title, fontsize=fsize)
    if legend:
        plt.legend(fontsize=fsize-4)
    if setlimits:
        plt.xlim((limits[0], limits[1]))
        plt.ylim((limits[2], limits[3]))

    
    