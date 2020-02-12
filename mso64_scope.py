# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 11:27:52 2020

@author: a6q
"""
import matplotlib.pyplot as plt
import numpy as np
import visa

rm = visa.ResourceManager()

addresses = rm.list_resources()
print(addresses)

scope_address = [a for a in addresses if a.startswith('USB0')][0]

dev = rm.open_resource(scope_address)

print(dev.query('*IDN?'))


dev.write(':DATA:SOURCE CH1')
dev.write(':DATa:START 1')
dev.write(':DATa:STOP 12500000')
#dev.write('WFMOutpre:NR_PT 100000')
dev.write(':WFMOutpre:ENCDG ASCII')
dev.write(':WFMOOutpre:BYT_NR 1')
#dev.write(':HEADER 0')


downsample = 10

print(dev.query('WFMOutpre:WFId?'))



signal_raw = np.array(dev.query(':CURVE?').split(','))
signal = signal_raw.astype(float)[::downsample]

def get_time_scale(signal, downsample=1):
    """Get the time-scale associated with the scope signal."""
    # get time-scale increment
    dt = float(dev.query('WFMOutpre:XINcr?'))
    # calculate the actual values of the x-scale
    t_scale = np.linspace(
            0,
            len(signal)*downsample*dt,
            num=int(len(signal))
            )
    return t_scale


time_scale = get_time_scale(signal, downsample=downsample)


plt.plot(time_scale, signal, lw=0.5)
fig = plt.gcf()
fig.set_size_inches(15,6)
plt.show()


#print(dev.read())

#dev.query('WFMOutpre:XUNIT?')
#dev.query('WFMOutpre:YUNIT?')

dev.close()

#dev.write('')
#dev.query('*IDN?')
#print(dev.read())