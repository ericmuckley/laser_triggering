# -*- coding: utf-8 -*-
"""

This script is for calibration if the Laseroptik AVACS beam attenuator.
Here we find a conversion between the angle of the AVACS and the
beam power in percent.

Created on Thu Mar 12 09:07:28 2020
@author: ericmuckley@gmail.com
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def logistic(x, x0, k, L):
    """Logistic function."""
    return L / (1 + np.exp(-k*(x-x0)))


def angle_to_percent(angle):
    """Convert attenuator angle to percent power with logistic function."""
    x0 = 28.1336
    k = -0.288186
    L = 0.994308 
    return 100 * (L / (1 + np.exp(-k*(angle-x0))))


def percent_to_angle(percent):
    """Convert attenuator percent power to angle with logistic function."""
    x0 = 28.1336
    k = -0.288186
    L = 0.994308 
    return x0 - np.log(100*L/percent - 1)/k







# all anges tested
angles_raw = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45])


# beam power read at each angle (three trials per angle for statistics)
'''
powers_raw = np.array([
    [8.1, 8.2, 8.9],
    [8.9, 8.8, 8.5],
    [9.0, 8.3, 9.0],
    [8.9, 8.6, 7.6],
    [8.2, 7.6, 8.3],
    [6.9, 5.7, 6.4],
    [3.3, 3.0, 3.1],
    [1.0, 1.03, 1.14],
    [0.1, 0.93, 0.96],
    [0.035, 0.032, 0.033]])

powers = np.mean(powers_raw, axis=1)
powers = (powers - np.min(powers)) / np.max(powers)
'''


powers = [1, 0.992395, 0.996198, 0.95057, 0.912548,
          0.718631, 0.353612, 0.11673, 0.0718631, 0]



# find initial fit parameters
guess = [np.median(angles_raw), 1, 1]
popt, pcov = curve_fit(logistic, angles_raw, powers, p0=guess)


angles = np.linspace(np.min(angles_raw), np.max(angles_raw), num=100)


fit = logistic(angles, *popt)


plt.plot(angles, fit, label='fit')
plt.scatter(angles_raw, powers, label='data')
plt.xlabel('Angle (deg)')
plt.ylabel('Power')
plt.legend()
plt.show()


