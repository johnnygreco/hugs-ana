#!/usr/bin/env python 

"""
Plot the current HSC footprint with Yang galaxy groups
and Lauer's BCG catalog.
"""

import os
import numpy as np
from astropy.table import Table
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
dataDIR = os.environ.get('DATA_DIR')
yangDIR = os.path.join(dataDIR, 'catalogs/Yang')
lauerDIR = os.path.join(dataDIR, 'catalogs/Lauer')
plt.style.use('jpg')
Ngal_min = 3
Ngal_max = 15
max_z = 0.1
cmap = plt.cm.rainbow

#############################
# get ra & dec from pointings 
#############################
fn = os.path.join(dataDIR, 'hsc/ObservedWidePointings.lst')
f = open(fn)
band = 'i'
ra = []
dec = []
for line in iter(f):
    data = line.split('|')
    if data[1][-1]==band:
        ra.append(float(data[2]))
        dec.append(float(data[3]))
ra = np.array(ra)
dec = np.array(dec)
out = np.vstack([ra, dec]).T 
print(len(ra), 'pointings')
outfile = os.path.join(dataDIR, 'HSC/HSC-'+str(band.upper())+'_wide_pointings.dat')
np.savetxt(outfile, out, fmt='%-13.12g')

#############################
# draw fields and pointings
#############################
fig, ax = plt.subplots(1,1)
for _ra, _dec in zip(ra, dec):
    #ax.scatter(ra, dec, alpha=0.1, zorder=5, color=cmap(0.0), label='HSC pointings')
    diam = 1.5
    ax.add_patch(Ellipse((_ra, _dec), diam, diam, color=cmap(0), alpha=0.1))

# fall equatorial
#ax.axhspan(ymin=-1., ymax=7, xmin=40/360., xmax=330/360., alpha=0.2, color='b', zorder=0)
# fall equatorial
#ax.axhspan(ymin=-7, ymax=-1., xmin=27.5/360., xmax=330/360., alpha=0.2, color='r', zorder=-1)
# spring equatorial 
#ax.axhspan(ymin=-2, ymax=5, xmin=127.5/360., xmax=225/360., alpha=0.4, color='g', zorder=1)
ax.set_xlabel(r'$\alpha$ [deg]')
ax.set_ylabel(r'$\delta$ [deg]')
ax.minorticks_on()
ax.set_ylim(-20,75)
ax.set_xlim(0,360)

yang = Table.read(yangDIR+'/yang_modelC_brightest.txt', format='ascii')
cut = (yang['Ngal'] >= Ngal_min) & (yang['Ngal'] <= Ngal_max)
cut &= yang['z'] <= max_z 
yang = yang[cut]
lauer = Table.read(lauerDIR+'/Lauer.txt', format='ascii')

#ax.scatter(lauer['ra'], lauer['dec'], c='r', marker='s', zorder=10)
ax.plot(yang['ra'], yang['dec'], color='gray', marker='.', zorder=-100, ls='none', alpha=0.1, label='Yang et al. 2007')

fig.savefig('/Users/protostar/Desktop/groups_in_footprint.png', dpi=300)

try: import RaiseWindow
except: pass
plt.show()
