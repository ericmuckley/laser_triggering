# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 15:00:38 2020

@author: ericmuckley@gmail.com
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm


plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['axes.linewidth'] = 3
plt.rcParams['xtick.minor.width'] = 3
plt.rcParams['xtick.major.width'] = 3
plt.rcParams['ytick.minor.width'] = 3
plt.rcParams['ytick.major.width'] = 3
plt.rcParams['figure.autolayout'] = True



def plot_setup(labels=['X', 'Y'], fsize=18, setlimits=False,
               limits=[0,1,0,1], title='', size=None, colorbar=False,
               legend=False, save=False, filename='plot.jpg'):
    """Creates a custom plot configuration to make graphs look nice.
    This can be called with matplotlib for setting axes labels,
    titles, axes ranges, and the font size of plot labels.
    This should be called between plt.plot() and plt.show() commands."""
    plt.xlabel(str(labels[0]), fontsize=fsize)
    plt.ylabel(str(labels[1]), fontsize=fsize)
    plt.title(title, fontsize=fsize)
    fig = plt.gcf()
    #if size:
    #    fig.set_size_inches(size[0], size[1])
    #else:
    #    fig.set_size_inches(10, 10)
    if legend:
        plt.legend(fontsize=fsize-4)
    if setlimits:
        plt.xlim((limits[0], limits[1]))
        plt.ylim((limits[2], limits[3]))
    if colorbar:
        plt.colorbar()
    if save:
        fig.savefig(filename, dpi=120, bbox_inches='tight')
        plt.tight_layout()


def stack_spectra(filelist):
    """Get a 2D array of stacked spectra and metadata in a dictionary."""
    d = {
        'colors': cm.jet(np.linspace(0, 1, len(filelist))),
        'labels': []}
    # loop over each spectrum and stack it into 2D array
    for fi, f in enumerate(filelist):
        df = pd.read_csv(f)
        d['labels'].append(os.path.split(f)[1].split('.csv')[0])
        # stack spectra together in a single matrix
        if fi == 0:
            d['spec_mat'] = np.array(df['Intensity'])
        else:
            d['spec_mat'] = np.column_stack((d['spec_mat'], df['Intensity']))
    d['wavelength'] = np.array(df['Wavelength'])
    return d
                             
                             

filelist = glob.glob(
    'C:\\Users\\a6q\\Documents\\GitHub\\laser_triggering\\support_files\\example_raman_csv_files/*')

d = stack_spectra(filelist)



for i in range(len(d['spec_mat'][0])):
    plt.plot(d['wavelength'], d['spec_mat'][:, i], label=d['labels'][i],
                     c=d['colors'][i], lw=1)
plt.legend()
plt.show()



# plot heatmap of Raman spectra over time
plot_extent = [
    0,
    len(d['labels']),
    np.min(d['wavelength']),
    np.max(d['wavelength'])]
plt.imshow(
    d['spec_mat'],
    aspect='auto',
    origin='lower',
    cmap='jet',    extent=plot_extent,
    vmin=np.min(d['spec_mat']),
    vmax=np.max(d['spec_mat']))
plot_setup(
    colorbar=True,
    title='Raman counts over time',
    labels=('Spectrum number', 'Wavelength (nm)'))
plt.show()




















