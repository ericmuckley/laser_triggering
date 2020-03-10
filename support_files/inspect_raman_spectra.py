# -*- coding: utf-8 -*-
"""

This module provides a method for linking Raman spectra with their
metadata as recorded in the log file.


Created on Tue Mar 10 10:13:42 2020
@author: ericmuckley@gmail.com
"""

import os
import pandas as pd
   

def create_raman_report(
        logfilename, raman_dir='C:\\Users\\Administrator\\Documents\\LightField\\csv_files'):
    """Create a dictionary which holds all Raman data and metadata from
    an experiment. The inputs should be the filename of the log file,
    and the directory in which Raman data is stored in .csv form."""
    # read log file
    log = pd.read_csv(logfilename)
    # create dictionary to hold all results, metadata, and statistics
    d = {'df': {}, 'log': log}
    max_int_list = []
    max_int_wl_list = []
    
    # loop over each raman file and save to dictionary
    for ri, r in enumerate(log['recent_raman_file']):
        # read raman data file
        df = pd.read_csv(os.path.join(raman_dir, r+'.csv'),
                         usecols=['Wavelength', 'Intensity'])
        # rename columns and add dataframe to dictionary
        df.columns = ['wl', 'int']
        d['df'][r] = df 
        # calculate some statistics and add to dictionary
        max_int_list.append(float(df['int'].max()))
        max_int_wl_list.append(float(df['wl'].iloc[df['int'].idxmax()]))
    d['log']['max_intensity'] = max_int_list
    d['log']['max_intensity_wavelength'] = max_int_wl_list
    return d 



if __name__ == '__main__':
    
    logfilename = 'C:\\Users\\Administrator\\Desktop\\eric\\laser_triggering\\logs\\2020-03-09_18-12-59.csv'


    d = create_raman_report(logfilename)

    '''
    # plot max intensity across grid
    plt.scatter(d['log']['x_position'],
                d['log']['y_position'],
                s=d['log']['max_intensity']/50,
                alpha=0.5)
    plt.show()
    '''
    
    '''
    # plot max intensity wavelength across grid
    plt.scatter(d['log']['x_position'],
                d['log']['y_position'],
                s=d['log']['max_intensity_wavelength']/5,
                alpha=0.5)
    plt.show()
    '''
    
    
    '''
    [plt.plot(d['df'][spec]['wl'], d['df'][spec]['int']) for spec in d['df']]
    plt.show()
    '''


  
'''
For serialization to JSON
for key in d:
    d[key]['df'] = d[key]['df'].to_json()
output = json.dumps(d)
'''