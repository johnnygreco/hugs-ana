#!/usr/bin/env python 
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
from astropy.table import Table
import hugs

bands = 'GI'
run_label = 'testrun'

stampdir = os.path.join(hugs.utils.hugs_pipe_io, 'stamps')
stampdir = os.path.join(stampdir, 'candies_'+run_label)

if not os.path.isdir(stampdir):
    catdir = os.path.join(hugs.utils.hugs_pipe_io, 'testing')
    cat_fn = os.path.join(catdir, 'master_testing_2.cat')
    cat = Table.read(cat_fn, format='ascii')
    cat = hugs.selection.cutter(cat)
    hugs.tasks.get_candy_stamps(cat, label=run_label, bands=bands)
else:
    cat = Table.read(os.path.join(stampdir, 'candy.cat'), format='ascii')

stamp_files = [f for f in os.listdir(stampdir) if
               f.split('-')[-1]=='wide.fits']
stamp_files = sorted(stamp_files, key=lambda f: int(f.split('-')[1]))
stamp_files = hugs.utils.grouper(stamp_files, len(bands))


fitdir = os.path.join(stampdir, 'imfit')
hugs.utils.mkdir_if_needed(fitdir)

for candy_files in stamp_files:

    candy_nums = np.array([int(f.split('-')[1]) for f in candy_files])
    assert np.alltrue(candy_nums==candy_nums[0])
    num = candy_nums[0]

    # fit i-band data first
    fn_iband = [f for f in candy_files if f.split('-')[2]=='i'][0]
    fn_iband = os.path.join(stampdir, fn_iband)
    prefix = os.path.join(fitdir, 'candy-{}-i'.format(num))
    sersic_i = hugs.tasks.fit_gal(fn_iband, prefix=prefix, 
                                  visualize=True, band='i')

    # perform forced photometry on other bands
    fn_other_bands = [f for f in candy_files if f.split('-')[2]!='i']
    init_params = {'X0': [sersic_i.X0, 'fixed'], 
                   'Y0': [sersic_i.Y0, 'fixed'],
                   'n': [sersic_i.n, 'fixed'],
                   'PA': [sersic_i.PA, 0, 360],
                   'ell': [sersic_i.ell, 0, 0.99],
                   'r_e': sersic_i.r_e, 
                   'I_e': sersic_i.I_e}
    for fn in fn_other_bands:
        band = fn.split('-')[2]
        fn = os.path.join(stampdir, fn)
        prefix = os.path.join(fitdir, 'candy-{}-{}'.format(num, band))
        sersic = hugs.tasks.fit_gal(fn, prefix=prefix,
                                    init_params={},#init_params,
                                    visualize=True, band=band)
        
