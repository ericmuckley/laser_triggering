# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 16:39:14 2020

@author: a6q
"""
import matplotlib.pyplot as plt
import numpy as np
import time


filenames = ['C:\\Users\\a6q\\exp_data\\2019 January 24 12_09_48.spe',
             'C:\\Users\\a6q\\exp_data\\2019 January 23 16_25_39-SG-raw.spe']
    
    
def load_spe(filename):
    """Load an spe file from Princeton Instruments as a numpy array."""
    def read_at(data, pos, size, ntype):
        raw.seek(pos)
        return np.fromfile(raw, ntype, size)
    raw = open(filename, 'rb')
    xdim = np.int64(read_at(raw, 42, 1, np.int16)[0])
    ydim = np.int64(read_at(raw, 656, 1, np.int16)[0])
    arr = read_at(raw, 4100, xdim*ydim, np.uint16)
    arr = arr.reshape((ydim, xdim))
    print('data shape: {}'.format(np.shape(arr)))
    if np.shape(arr)[0] == 1:
        arr = arr[0]
    print('data shape: {}'.format(np.shape(arr)))
    return arr



for f in filenames:
    
    spec = load_spe(f)
    
    plt.plot(spec)
    plt.show()

    
    
    
    
    