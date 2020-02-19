# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 13:05:47 2020

@author: Administrator
"""

import pandas as pd
import numpy as np

filename = r'C:\Users\Administrator\Desktop\eric\laser_triggering\logs\2020-02-11_13-05-06.csv'

df = pd.read_csv(filename)

df.replace('', np.nan, inplace=True)
df.dropna(how='all', inplace=True)