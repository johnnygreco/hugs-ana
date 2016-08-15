#!/usr/bin/env python 

"""
Plot the current HSC footprint with Yang galaxy groups
and Lauer's BCG catalog.
"""

import os
import numpy as np
from astropy.table import Table
import matplotlib.pyplot as plt
dataDIR = os.environ.get('DATA_DIR')
yangDIR = os.path.join(dataDIR, 'catalogs/Yang')
lauerDIR = os.path.join(dataDIR, 'catalogs/Lauer')
plt.style.use('jpg')
Ngal_min = 4
cmap = plt.cm.rainbow

#############################
# get ra & dec from pointings 
#############################
fn = os.path.join(dataDIR, 'hsc/ObservedWidePointings.lst')
f = open(fn)
band = 'g'
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
#np.savetxt('output/HSC_wide_pointings.dat', out)

#############################
# draw fields and pointings
#############################
fig, ax = plt.subplots(1,1)
ax.scatter(ra, dec, alpha=0.1, zorder=5, color=cmap(0.0), label='HSC pointings')
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
yang = yang[yang['Ngal'] >= Ngal_min]
lauer = Table.read(lauerDIR+'/Lauer.txt', format='ascii')

#ax.scatter(lauer['ra'], lauer['dec'], c='r', marker='s', zorder=10)
ax.plot(yang['ra'], yang['dec'], color='gray', marker='.', zorder=-100, ls='none', alpha=0.1, label='Yang et al. 2007')

fig.savefig('/Users/protostar/Desktop/groups_in_footprint.png', dpi=300)

try: import RaiseWindow
except: pass
plt.show()


