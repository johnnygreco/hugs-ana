#!/usr/bin/env python 
"""
Preliminary HSC-HUGs detection pipeline. 
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import shutil
import time

from scipy import ndimage
from astropy.io import fits

from imtools import replace_with_sky
import sexpy

#########################################
# Pipeline parameters
#########################################
BACK_SIZE = 128
HI_THRESH = 9.0
LO_THRESH_1 = 0.5
LO_THRESH_2 = 0.7
ASSOC_RADIUS = 20.0
#########################################

def main(relpath, run_label, results_dir='results', make_ds9reg=False, 
         view_with_ds9=False, log_fn=None, clean=None, verbose=False, **kwargs):

    if log_fn is not None:
        # write stdout to log
        import sys
        logfile = open(log_fn, 'a')
        sys.stdout = logfile
        stdout = sys.stdout

    print('*******************************')
    print('**** Running HUGs Pipeline ****')
    print('****', time.strftime("%m/%d/%y"), '---',
          time.strftime("%H:%M:%S"), '****')
    print('*******************************')

    created_files = []
    sex_verbose = 'NORMAL' if verbose else 'QUIET'
    param_fn = run_label+'.param' # create unique param file

    # detect bright sources
    step = 'bright'
    config = {'DETECT_THRESH': HI_THRESH,
              'DETECT_MINAREA': 3,
              'BACK_SIZE': BACK_SIZE, 
              'VERBOSE_TYPE': sex_verbose,
              'PARAMETERS_NAME': param_fn}
    params = ['X_IMAGE', 'Y_IMAGE', 'MAG_AUTO']
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    sw.set_check_images(['b', 'brms'], prefix=step+'-')
    check_files = [sw.get_outdir(f) for f in 
                   sw.get_config()['CHECKIMAGE_NAME'].split(',')]
    bright_cat = step+'.cat'
    if verbose:
        sw.print_config()
        sw.print_params()
    sw.run('img.fits', cat=bright_cat)

    created_files.extend(check_files)
    created_files.append(sw.get_outdir(bright_cat))
    del sw
    #######################

    # find faint sources associated with the bright ones
    step = 'assoc'
    config = {'ASSOC_NAME': bright_cat,
              'ASSOC_PARAMS': '1,2,3',
              'ASSOC_TYPE': 'MAG_MEAN',
              'ASSOC_RADIUS': ASSOC_RADIUS,
              'ASSOC_DATA': '1,2,3',
              'ASSOCSELEC_TYPE': 'MATCHED',
              'DETECT_THRESH': LO_THRESH_1,
              'BACK_SIZE': BACK_SIZE, 
              'VERBOSE_TYPE': sex_verbose, 
              'PARAMETERS_NAME': param_fn}
    params = ['X_IMAGE', 'Y_IMAGE','MAG_AUTO']+\
             ['VECTOR_ASSOC('+str(i)+')' for i in range(1,4)]
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    sw.set_check_images('s', prefix=step+'-')
    check_files = [sw.get_outdir(f) for f in 
                   sw.get_config()['CHECKIMAGE_NAME'].split(',')]
    assoc_cat = step+'.cat'
    if verbose:
        sw.print_config()
        sw.print_params()
    sw.run('img.fits', cat=assoc_cat)

    created_files.extend(check_files)
    created_files.append(sw.get_outdir(assoc_cat))

    # replace assoc regions with sky noise
    new_img_fn = sw.get_indir('img_seg_skynoise.fits')
    replace_with_sky(
        sw.get_indir('img.fits'), sw.get_outdir(step+'-SEGMENTATION.fits'),
        sw.get_outdir('bright-BACKGROUND_RMS.fits'), sw.get_outdir('bright-BACKGROUND.fits'),
        write=new_img_fn, dilator=11)
    created_files.append(new_img_fn)
    del sw
    #######################

    # detect sources
    step = 'detect'
    config = {'DETECT_THRESH': LO_THRESH_2,
              'FILTER_NAME': 'gauss_15.0_31x31.conv',
              'BACK_SIZE': BACK_SIZE,
              'VERBOSE_TYPE': sex_verbose,
              'PHOT_APERTURES': '3,4,5,6,7,8,16,32', 
              'PARAMETERS_NAME': param_fn}
    sw = sexpy.SexWrapper(config, relpath=relpath)
    sw.set_check_images(['a', 'f'], prefix=step+'-')
    check_files = [sw.get_outdir(f) for f in 
                   sw.get_config()['CHECKIMAGE_NAME'].split(',')]
    if verbose:
        sw.print_config()
        sw.print_params()
    detect_cat = step+'.cat'
    sw.run(new_img_fn.split('/')[-1], cat=detect_cat)

    created_files.extend(check_files)
    created_files.append(sw.get_outdir(detect_cat))
    #######################

    # save final catalog in ascii format
    cat = sexpy.read_cat(sw.get_outdir(detect_cat))
    # sigma from Lauren's work
    sigma = 1e11*10**(-0.4*cat['MU_MAX'])*10**(-0.4*cat['MAG_ISO'])
    sigma /= (10**(-0.4*cat['MU_THRESHOLD'])*cat['ISO0'])
    cat['SIGMA'] = sigma
    outfile = os.path.join(results_dir, run_label+'_full_cat.txt')
    cat.write(outfile, format='ascii')
    created_files.append(outfile)
    #######################

    if make_ds9reg:
        regfile = outfile[:-4]+'.reg'
        sexpy.cat_to_ds9reg(cat, outfile=regfile, **kwargs)
        created_files.append(regfile)
    if view_with_ds9:
        from toolbox.utils import ds9view
        ds9view(sw.get_indir('img.fits'), regfile)
    
    # do some bookkeeping and delete unwanted files
    if verbose: print('created files:\n'+'\n'.join(created_files))
    if clean=='all':
        if verbose: print('deleting:')
        for path in created_files:
            if 'results' not in path.split('/'):
                if verbose: print(path)
                os.remove(path)
        path = sw.get_sexout(relpath.split('/')[0])
        if verbose: print(path)
        shutil.rmtree(path)
    elif clean=='fits':
        if verbose: print('deleting:')
        for path in created_files:
            if 'fits'==path[-4:]:
                if verbose: print(path)
                os.remove(path)
    elif clean is not None:
        print('**** invalid cleaning option ****')
    if verbose: print('deleting:', sw.get_configdir(param_fn))
    os.remove(sw.get_configdir(param_fn)) # delete unique param file
    #######################

    if log_fn is not None:
        # switch stdout back
        logfile.close()
        sys.stdout = stdout

if __name__=='__main__':
    # get command-line args
    from parser import parse_args
    band, tract, patch, args = parse_args()
    relpath = 'HSC-'+band+'/'+str(tract)+'/'+patch[0]+'-'+patch[-1]
    run_label = 'HSC-'+band+'_'+str(tract)+'_'+patch
    main(relpath, run_label, make_ds9reg=True, view_with_ds9=True,
         textparam=args.text_param, clean=args.clean, verbose=args.verbose)
