#!/usr/bin/env python 

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib.patches import Ellipse
from toolbox.image import zscale
import hugs
import sexpy
import seaborn
seaborn.set(font_scale=1.6)
seaborn.set_style('white')

sexout = '/Users/protostar/local_data/SExIO/sexout/HSC-I/9348/7-6/'
sexin = '/Users/protostar/local_data/SExIO/sexin/HSC-I/9348/7-6/'

imgfile = sexin+'img.fits'
img2file= sexin+'img_seg_skynoise.fits'
maskfile = sexin+'bad.fits'

img = fits.open(imgfile)[0]
img2 = fits.open(img2file)[0]
mask = fits.getdata(maskfile)
img2.data *= (mask==0)

fig, axes = plt.subplots(2,2,figsize=(10.5, 14))
axes = axes.flatten()
fig.subplots_adjust(wspace=0.08, hspace=0.15)

images = [img, img2, img2, img2]
x0, y0 = 180.14925, -0.29423337
x0_image, y0_image = 2775.4493, 3733.4678
size=650

for i, ax in zip(images, axes):
    img_co = hugs.imtools.cutout(i.data, (x0, y0), i.header, size=size)
    vmin, vmax = zscale(i.data)
    ax.imshow(img_co.data, origin='lower', aspect='equal', 
              cmap=plt.cm.gray_r, vmin=-0.08, vmax=0.2)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

cat = sexpy.read_cat(sexout+'detect.cat')
for c in cat:
    A_diam, B_diam = 2*c['A_IMAGE'], 2*c['B_IMAGE']
    axes[2].add_patch(Ellipse((c['X_IMAGE']-(x0_image-size/2)-1, c['Y_IMAGE']-(y0_image-size/2)-1),
                               3*A_diam, 3*B_diam, c['THETA_IMAGE'], 
                               fc='none', lw=1.5, ec='#83F52C'))
cat = hugs.apply_cuts(cat, z=0.06, sb_lo=None)
for c in cat:
    A_diam, B_diam = 2*c['A_IMAGE'], 2*c['B_IMAGE']
    axes[3].add_patch(Ellipse((c['X_IMAGE']-(x0_image-size/2)-1, c['Y_IMAGE']-(y0_image-size/2)-1),
                               3*A_diam, 3*B_diam, c['THETA_IMAGE'], 
                               fc='none', lw=1.5, ec='#83F52C'))

try: import RaiseWindow
except: pass
plt.show()

fig.savefig('/Users/protostar/Desktop/pipe_steps.pdf', bbox='tight')
