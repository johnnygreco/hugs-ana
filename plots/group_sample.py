#!/usr/bin/env python 

from __future__ import division, print_function

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from astropy import units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord
from spherical_geometry.polygon import SphericalPolygon
from toolbox.cosmo import Cosmology
from toolbox.utils.plotting import line_widths
import hugs
cmap = plt.cm.rainbow
plt.style.use('seaborn-talk')
cosmo = Cosmology()

datadir = '../results/'
fn = 'cat_z0.065_Mh13.0-14.0_group_info.txt'
groups = Table.read(datadir+fn, format='ascii')
coords = SkyCoord(ra=groups['ra']*u.degree, 
                  dec=groups['dec']*u.degree, 
                  frame='icrs')
ra_rad = coords.ra.wrap_at(180*u.deg).radian
dec_rad = coords.dec.radian

f1, a1 = plt.subplots(subplot_kw={'projection':'aitoff'}, figsize=(8,4.2))
f1.subplots_adjust(top=0.95,bottom=0.0)
a1.grid(True)
a1.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)
a1.set_xticks([-np.pi/2, 0, np.pi/2])

groups['D_A'] = cosmo.D_A(groups['z'])
groups['r180'] = hugs.datasets.yang.r180(groups['Mh_Lest'], groups['z'])
groups['theta_180'] = np.rad2deg((groups['r180']/groups['D_A']))
z_cmap = (groups['z']-groups['z'].min())/(groups['z'].max()-groups['z'].min())

pointings = hugs.datasets.hsc.load_pointings('i')
f2, a2 = plt.subplots(5,1, figsize=(10, 13))
f2.subplots_adjust(hspace=0.1, right=0.8)
a2 = a2.flatten()

ralim = [[223, 253], [125, 155], [165, 195], [200, 230], [325, 355]] 
declim = [[40, 47], [-2, 5], [-4, 3], [-3.5, 3.5], [-2, 5]]

# norm is a class which, when called, can normalize data into the
# [0.0, 1.0] interval.
norm = plt.Normalize(vmin=groups['z'].min(), vmax=groups['z'].max())
# choose a colormap
c_m = plt.cm.rainbow
# create a ScalarMappable and initialize a data structure
s_m = plt.cm.ScalarMappable(cmap=c_m, norm=norm)
s_m.set_array([])

for i in range(len(a2)):
    a2[i].set_aspect('equal')
    cut = (pointings['ra'] < ralim[i][1])
    cut &= (pointings['ra'] > ralim[i][0])
    cut &= (pointings['dec'] < declim[i][1])
    cut &= (pointings['dec'] > declim[i][0])
    for ra, dec in pointings[cut]['ra', 'dec']:
        diam = 1.5
        a2[i].add_patch(
            Ellipse((ra, dec), diam, diam, color='gray', alpha=0.05))
    cut = (groups['ra'] < ralim[i][1]) & (groups['ra'] > ralim[i][0])
    cut &= (groups['dec'] < declim[i][1]) & (groups['dec'] > declim[i][0])
    for g in groups[cut]:
        cone = SphericalPolygon.from_cone(
            g['ra'], g['dec'], 2*g['theta_180'], steps=30)
        ra, dec = list(cone.to_radec())[0]
        ra = ra + 360*(ra<0)
        a2[i].plot(ra, dec, c=s_m.to_rgba(g['z']), lw=1.8)
    a2[i].scatter(groups[cut]['ra'], groups[cut]['dec'], color='k', alpha=0.7)
    a2[i].set_xlim(ralim[i])
    a2[i].set_ylim(declim[i])
    a2[i].minorticks_on()
    a2[i].tick_params(labelsize=12)
    a2[i].set_ylabel(r'$\delta$ [deg]')

a2[-1].set_xlabel(r'$\alpha$ [deg]')
cbar_ax = f2.add_axes([0.84, 0.28, 0.03, 0.4])
f2.colorbar(s_m, cax=cbar_ax)
cbar_ax.set_ylabel(r'$z$')
f2.savefig('../figures/groups_2r180_cones.pdf', bbox_inches='tight')

f3, a3 = plt.subplots()
for ra, dec in pointings['ra', 'dec']:
    diam = 1.5
    a3.add_patch(Ellipse((ra, dec), diam, diam, color='gray', alpha=0.05))
a3.scatter(groups['ra'], groups['dec'], color='k', alpha=0.7)

import RaiseWindow
plt.show()
