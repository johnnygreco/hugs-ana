#!/usr/bin/env python 

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from toolbox.image import zscale

import hugs
from sexpy import SEX_IO_DIR

sexin = os.path.join(SEX_IO_DIR, 'sexin')

cat = Table.read('../results/final_test_cat.txt', format='ascii')

mask = np.zeros(len(cat), dtype=bool)

for i, c in enumerate(cat):
    ra, dec = c['ALPHA_J2000'], c['DELTA_J2000']
    tract, patch = c['tract'], c['patch']
    relpath = 'HSC-I/'+str(tract)+'/'+patch
    imgfile = os.path.join(os.path.join(sexin, relpath), 'img.fits')
    img = fits.open(imgfile)[0]

    cutout = hugs.imtools.cutout(img.data, [ra, dec], img.header)
    zmin, zmax = zscale(cutout.data)

    f, a = plt.subplots()
    a.imshow(cutout.data, vmin=zmin, vmax=zmax, cmap=plt.cm.gray_r)
    try: import RaiseWindow
    except: pass
    plt.show()

    keep = input('keep? ')

    if keep in ['yes', 'y']:
        mask[i] = True

print('final cat:')
print(cat[mask])
