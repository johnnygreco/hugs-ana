#!/usr/bin/env python 

import os
import argparse

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Ellipse
from astropy.io import fits
from astropy.table import Table
import seaborn
seaborn.set(font_scale=1.6)
seaborn.set_style('white')

import hugs
from sexpy import SEX_IO_DIR
from toolbox.image import zscale

parser = argparse.ArgumentParser()
parser.add_argument('group_id', type=str)
args = parser.parse_args()
results_dir = '../results/group_'+args.group_id+'/'

sexin = os.path.join(SEX_IO_DIR, 'sexin')
cat = Table.read(results_dir+'selection_cat.txt', format='ascii')
mask = np.zeros(len(cat), dtype=bool)

class MyButtons(object):
    def keep(self, event):
        mask[i] = True
        plt.close()
    def discard(self, event):
        plt.close()
    def get_info(self, event):
        print(cat['ALPHA_J2000', 'DELTA_J2000', 'MAG_AUTO',\
                  'FLUX_RADIUS', 'ISO0', 'SIGMA', 'FLAGS',\
                  'MU_APER_2', 'MU_APER_4'][i])
    def save(self, event):
        print('saving image...')
        f.savefig('../figures/group_'+args.group_id+'_cand'+str(i)+'.pdf')

buttons = MyButtons()
numcand = len(cat)
for i, c in enumerate(cat):
    ra, dec = c['ALPHA_J2000'], c['DELTA_J2000']
    tract, patch = c['tract'], c['patch']
    relpath = 'group_'+args.group_id+'/HSC-I/'+str(tract)+'/'+patch
    imgfile = os.path.join(os.path.join(sexin, relpath), 'img.fits')
    img = fits.open(imgfile)[0]

    cutout = hugs.imtools.cutout(img.data, [ra, dec], img.header)
    zmin, zmax = zscale(cutout.data)

    f, a = plt.subplots()

    a.imshow(cutout.data, vmin=zmin, vmax=zmax, cmap=plt.cm.gray_r,
             origin='lower', aspect='equal')

    y0, x0 = cutout.shape[0]//2, cutout.shape[0]//2
    A_diam, B_diam = 2*c['A_IMAGE'], 2*c['B_IMAGE']
    a.add_patch(Ellipse((x0, y0), 3*A_diam, 3*B_diam, c['THETA_IMAGE'],
                        fc='none', lw=3.0, ec='c', ls='--'))

    axkeep = plt.axes([0.82, 0.6, 0.13, 0.075])
    axdiscard = plt.axes([0.82, 0.5, 0.13, 0.075])
    axinfo = plt.axes([0.82, 0.25, 0.13, 0.075])
    axsave = plt.axes([0.82, 0.15, 0.13, 0.075])

    bkeep = Button(axkeep, 'Keep', color='g')
    bkeep.on_clicked(buttons.keep)
    bdiscard = Button(axdiscard, 'Discard', color='r')
    bdiscard.on_clicked(buttons.discard)
    binfo = Button(axinfo, 'info', color='y')
    binfo.on_clicked(buttons.get_info)
    bsave = Button(axsave, 'save', color='b')
    bsave.on_clicked(buttons.save)

    a.set_title('candidate '+str(i)+' of '+str(numcand))
    plt.setp(a.get_xticklabels(), visible=False)
    plt.setp(a.get_yticklabels(), visible=False)

    try: import RaiseWindow
    except: pass
    plt.show()

cat = cat[mask]
cat.write(results_dir+'viz_cat.txt', format='ascii')
print('final cat after viz:')
print(cat)
