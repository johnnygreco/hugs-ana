#!/usr/bin/env python 

from __future__ import print_function

import os
import numpy as np
from sex import runsex, kernals, config

def run(group_id):
    """
    Run sextractor on images associated with galaxy group.
    """
    relpath = 'group_'+str(group_id)
    imgfiles = [d for d in os.listdir('sexin/'+relpath) if 'img' in d]
    wtsfiles = [d for d in os.listdir('sexin/'+relpath) if 'wts_bad' in d]
    config['CHECKIMAGE_TYPE'] = 'NONE'
    for img_file, wts_file in zip(imgfiles, wtsfiles):
        prefix = img_file[:-8]
        config['WEIGHT_IMAGE'] = wts_file
        runsex(img_file, cat=prefix+'sex.cat', relpath=relpath, **config)

def combine_cats(group_id, min_sep=0.7):
    """
    Combine the catalogs into one master cat. 
    min_sep = separation at which two objects are 
    considered the same. Default is 0.7", which is 
    roughly the FWHM. 
    """
    from astropy.table import Table, vstack
    from toolbox.utils import read_sexout
    from toolbox.astro import angsep
    path = 'sexout/group_'+str(group_id)+'/'
    catfiles = [d for d in os.listdir(path) if 'sex.cat' in d]
    tract = catfiles[0].split('_')[1]
    patch = catfiles[0].split('_')[2]
    cat = read_sexout(path+catfiles[0])
    cat['tract'] = [int(tract)]*len(cat)
    cat['patch'] = [patch]*len(cat)
    for f in catfiles[1:]:
        tempcat = read_sexout(path+f)
        tract = f.split('_')[1]
        patch = f.split('_')[2]
        tempcat['tract'] = [int(tract)]*len(tempcat)
        tempcat['patch'] = [patch]*len(tempcat)
        cat = vstack([cat, tempcat])
    print(len(cat), 'objects in initial master catalog')

    ###############################################
    # build mask for double entries. consider 
    # object within 0.7" (the fwhm) the same object
    ###############################################
    mask = np.ones(len(cat), dtype=bool)
    for i, (ra, dec) in enumerate(cat['ALPHA_J2000','DELTA_J2000']):
        # don't search objects flagged as double entries
        if mask[i]==True:
            seps = angsep(ra, dec, cat['ALPHA_J2000'], cat['DELTA_J2000'])
            unique = seps > minsep
            unique[i] = True # it will certainly match itself
            mask &= unique   # double entries set to False
    cat = cat[mask]
    print(len(cat), 'objects after removing double entries with min sep =',
          minsep, 'arcsec')
    cat.write(path+'master.cat', format='ascii')

if __name__=='__main__':
    group_id = 8453
    print('searching around group', group_id)
    run(group_id)
    print('combining catalogs into master.cat')
    combine_cats(group_id)
