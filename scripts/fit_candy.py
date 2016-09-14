#!/usr/bin/env python 
"""
Use hugs.phot and hugs.imfit to do fit udg candidates.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os

import numpy as np
from astropy.table import Table, vstack
import astropy.units as u

import hugs
from toolbox.cosmo import Cosmology
from toolbox.image import zscale
cosmo = Cosmology()
dataDIR = os.path.join(os.environ.get('DATA_DIR'), 'HSC/candy_cutouts')
results_dir = '../results/'
group_ids = [1925, 3765, 4736, 6112, 8453, 12885, 7572, 8524, 9436]
group_info = hugs.datasets.load_yang_groups()

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

for idx in sorted_idx:
    fn = ifiles[idx]
    print(fn)
