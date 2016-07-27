#!/usr/bin/env python 

"""
Explore the influence of the SExtractor 
configuration parameters.
"""

from __future__ import print_function 

import os
from sexpy import SexWrapper

def explore(tract, patch, band='I'):

    relpath = 'HSC-'+band+'/'+tract+'/'+patch[0]+'-'+patch[-1]+'/'

    fixed_config = {'WEIGHT_IMAGE': 'wts_bad.fits',
                    'WEIGHT_TYPE' : 'MAP_WEIGHT',
                    'FILTER_NAME' : 'gauss_5_31x31.conv'}

    sw = SexWrapper(fixed_config)
            

    detect_thresh = [2.0]#, 1.5, 1.0, 0.9, 0.8]
    for dt in detect_thresh:
        sw.set_config('DETECT_THRESH', dt)
        cat = 'DETECT_THRESH_'+str(dt)+'.cat'
        sw.run('img.fits', cat=cat, relpath=relpath)

    sw.reset_config()
    sw.write_config('../sexout/'+relpath+'fixed_config.sex')

if __name__ =='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tract', type=str)
    parser.add_argument('patch', type=str)
    args = parser.parse_args()
    explore(args.tract, args.patch)
