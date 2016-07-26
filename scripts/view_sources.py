#!/usr/bin/env python 

import os
from astropy.table import Table

def make_ds9reg(group_id, **kwargs):
    from toolbox.utils import read_sexout, sexout_to_ds9reg
    path = 'sexout/group_'+str(group_id)
    files = [f for f in os.listdir(path) if (('HSC' in f) and (f[-3:]=='cat'))]
    regfiles = []
    for f in files:
        fn = os.path.join(path, f)
        table = read_sexout(fn)
        fn = fn[:-4]+'.reg'
        sexout_to_ds9reg(table, outfile=fn, **kwargs)
        regfiles.append(fn)
    return regfiles

def view(group_id, regfiles=None, **kwargs):
    from toolbox.utils import ds9view
    path = 'sexin/group_'+str(group_id)
    files = [f for f in os.listdir(path) if 'img' in f]
    for i, f in enumerate(files):
        fn = os.path.join(path, f)
        if regfiles is not None:
            reg = regfiles[i]
        else:
            reg = None
        ds9view(fn, reg)
        raw_input("Press Enter to continue...")

if __name__=='__main__':
    group_id = 3765
    textparam = 'MAG_AUTO'
    regfiles = make_ds9reg(group_id, textparam=textparam)
    view(group_id, regfiles)
