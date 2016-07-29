#!/usr/bin/env python 

"""
Explore the influence of the SExtractor configuration parameters.
"""

from __future__ import print_function 

import os
import sexpy

def explore(tract, patch, band='I'):

    relpath = 'HSC-'+band+'/'+tract+'/'+patch[0]+'-'+patch[-1]+'/'

    sw = sexpy.SexWrapper()
            
    print('**** testing influence of DETECT_THRESH ****')
    detect_thresh = [2.0, 1.5, 1.0, 0.9, 0.8, 0.7]
    for thresh in detect_thresh:
        testparam = 'DETECT_THRESH'
        sw.set_config(testparam, thresh)
        prefix = testparam+'_'+str(thresh)+'_'
        sw.set_check_images('a', prefix=prefix)
        cat = testparam+'_'+str(thresh)+'.cat'
        sw.run('img.fits', cat=cat, relpath=relpath)
    sw.reset_config()

    print('**** testing influence of DETECT_MINAREA ****')
    detect_minarea = [3, 5, 10, 50, 100, 500]
    for min_area in detect_minarea:
        testparam = 'DETECT_MINAREA'
        sw.set_config(testparam, min_area)
        prefix = testparam+'_'+str(min_area)+'_'
        sw.set_check_images('a', prefix=prefix)
        cat = testparam+'_'+str(min_area)+'.cat'
        sw.run('img.fits', cat=cat, relpath=relpath)
    sw.reset_config()

    print('**** testing influence of DEBLEND_NTHRESH ****')
    deblend_nthresh = [1, 2, 8, 16, 32, 64]
    for n_thresh in deblend_nthresh:
        testparam = 'DEBLEND_NTHRESH'
        sw.set_config(testparam, n_thresh)
        prefix = testparam+'_'+str(n_thresh)+'_'
        sw.set_check_images('a', prefix=prefix)
        cat = testparam+'_'+str(n_thresh)+'.cat'
        sw.run('img.fits', cat=cat, relpath=relpath)
    sw.reset_config()

    print('**** test influence of DEBLEND_MINCONT ****')
    deblend_mincont = [0.5, 0.1, 0.01, 0.005, 0.0005, 0.00005]
    for min_cont in deblend_mincont:
        testparam = 'DEBLEND_MINCONT'
        sw.set_config(testparam, min_cont)
        prefix = testparam+'_'+str(min_cont)+'_'
        sw.set_check_images('a', prefix=prefix)
        cat = testparam+'_'+str(min_cont)+'.cat'
        sw.run('img.fits', cat=cat, relpath=relpath)
    sw.reset_config()
    sw.write_config('../SExIO/sexout/'+relpath+'fixed_config.sex')

if __name__ =='__main__':
    from hugs.parser import parse_args
    args = parse_args()
    explore(args.tract, args.patch)
