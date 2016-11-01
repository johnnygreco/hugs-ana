#!/usr/bin/env python 

import os
import numpy as np
from astropy.table import Table, vstack
from hugs.utils import pixscale
import hugs

def main(group_id):

    # build master catalog
    label = 'group_{}'.format(group_id)
    master_dir = os.path.join(hugs.utils.hugs_pipe_io, 'master_cats')
    group_dir = os.path.join(hugs.utils.hugs_pipe_io, 'group_results')
    group_dir = os.path.join(group_dir, label)
    cat_fn = os.path.join(master_dir, label+'.cat')
    if not os.path.isfile(cat_fn):
        files = [f for f in os.listdir(group_dir) if f[-3:]=='cat']
        master_cat = Table()
        for fn in files:
            tract, patch = int(fn.split('-')[2]), fn.split('-')[3][:3]
            patch = patch[0]+'-'+patch[-1]
            fn = os.path.join(group_dir, fn)
            tab = Table.read(fn, format='ascii')
            tab['tract'] = [tract]*len(tab)
            tab['patch'] = [patch]*len(tab)
            master_cat = vstack([master_cat, tab])
        master_cat['id'] = np.arange(len(master_cat))
        master_cat.write(cat_fn, format='ascii')
    else:
        master_cat = Table.read(cat_fn, format='ascii')
    master_cat['a_3_sig'] = master_cat['semimajor_axis_sigma']*3*pixscale
    master_cat['r_circ'] = master_cat['equivalent_radius']*pixscale

    # make selection cuts
    cat = hugs.selection.cutter(master_cat, group_id=group_id)

    # fetch postage stamps (if needed) and perform fit
    hugs.tasks.fit_candy_stamps(label, cat=cat)

if __name__=='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('group', type=int, help='group id')
    args = parser.parse_args()
    main(args.group)
