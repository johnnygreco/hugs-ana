#!/usr/bin/env python3

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table, vstack
import astropy.units as u
from astropy.io import fits
plt.style.use('jpg')

import hugs
from toolbox.cosmo import Cosmology
from toolbox.image import zscale
cosmo = Cosmology()

saveDIR = os.path.join(os.environ.get('DROP_DIR'), 'talks/hsc-meeting-2016-talk/')
dataDIR = os.path.join(os.environ.get('DATA_DIR'), 'HSC/candy_cutouts')
results_dir = '../../results/'
group_ids = [1925, 3765, 4736, 6112, 8453, 12885, 7572, 8524, 9436]
group_info = hugs.datasets.yang.load_groups()

cands = Table()
for _id in group_ids:
    fn = results_dir+'group_'+str(_id)+'/viz_cat.txt'
    tab = Table.read(fn, format='ascii')
    tab['group_id'] = [_id]*len(tab)
    z = group_info['z'][int(_id)-1]
    D_A = cosmo.D_A(z)
    r_eff = tab['FLUX_RADIUS']*hugs.pixscale*u.arcsecond.to('radian')*D_A*1e3
    tab['r_eff'] = r_eff
    cands = vstack([cands, tab])
mask = hugs.doubles_mask(cands)
cands = cands[mask]
sorted_idx = cands['r_eff'].argsort()[::-1]

ifiles = [f for f in os.listdir(dataDIR) if 'HSC-I' in f]
ifiles = sorted(ifiles, key=lambda f: int(f.split('-')[0]))
ifiles = np.array([os.path.join(dataDIR, f) for f in ifiles])
ifiles = ifiles[mask]
cands = cands[sorted_idx]

for i in range(len(ifiles)):
    f1, a1 = plt.subplots()
    img = fits.getdata(ifiles[sorted_idx[i]])
    img = hugs.imtools.cutout(img, (img.shape[0]/2,img.shape[1]/2), size=200).data
    print(i+1, cands['ALPHA_J2000'][i], cands['DELTA_J2000'][i])
    vmin, vmax = zscale(img)
    a1.imshow(img, vmin=vmin, vmax=vmax, aspect='equal', origin='lower', cmap=plt.cm.gray_r)
    plt.setp(a1.get_xticklabels(), visible=False)
    plt.setp(a1.get_yticklabels(), visible=False)
    f1.savefig(saveDIR+'stamps/cand_'+str(i+1)+'.pdf', bbox='tight')
    #print(i+1, ifiles[sorted_idx[i]])
