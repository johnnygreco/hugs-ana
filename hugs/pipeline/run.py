"""
This is an experimental pipeline. Will refactor when 
I converge on the best algorithm. 
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
import numpy as np

import time
import sexpy
from .. import imtools
from ..apply_cuts import apply_cuts

__all__ = ['run', 'STEPS']

STEPS = ['bright', 'assoc', 'clean']

IMG_RUN_FILES = {STEPS[0]  : 'img.fits', 
                 STEPS[1]  : 'img.fits', 
                 STEPS[2]  : 'img_clean.fits'}

def _start_sex(step, config, relpath):
    print('\n***** executing step:', step)

    # get non-sextractor config options (all lowercase)
    params = config.pop('params', sexpy.MY_DEFAULT_PARAMS)
    check_imgs = config.pop('set_check_images', None)
    
    # setup sextractor wrapper
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    if check_imgs is not None:
        sw.set_check_images(check_imgs, prefix=step+'-')
    sw.print_config()
    sw.print_params()

    # run sextracor
    sw.run(IMG_RUN_FILES[step], cat=step+'.cat')

    return sw

def run(relpath, pipe_steps, run_label, log_fn=None, results_dir='',
        make_ds9reg=False, view_with_ds9=False, clean=False, **kwargs):
    """
    Run the HUGs pipeline.

    Parameters
    ----------
    relpath : string
        Relative path for SExtractor in/out directories.
        See the doc string for the SexWrapper class of sexpy.
    pipe_steps : tuple, (bool, string, dict)
        (do step True/False, step name, sex config)
    run_label : string
        A label for this pipeline run.
    log_fn : string, optional
        If not None, the log file name to write stdout to.
    results_dir : string, optional
        The directory to output the final catalog. Default 
        is the current directory. 
    make_ds9reg : bool
        If True, convert at into a ds9 regions file.
    view_with_ds9 : bool
        If True, view final catalog with ds9.
    clean : bool
        If True, delete all files created by pipeline.
    **kwargs : dict
        Optional input parameters for sexpy.cat_to_ds9reg.
    """
    if log_fn is not None:
        # write stdout to log
        logfile = open(log_fn, 'a')
        sys.stdout = logfile
        stdout = sys.stdout

    print('*******************************')
    print('**** Running HUGs Pipeline ****')
    print('****', time.strftime("%m/%d/%y"), '---',
          time.strftime("%H:%M:%S"), '****')
    print('*******************************')

    ###############################################
    # Loop over all steps of pipeline
    ###############################################

    new_files = []

    step_num = 0
    step = STEPS[step_num]
    do_step, config = pipe_steps[step]
    if do_step:
        sw = _start_sex(step, config, relpath)
        #img_fn = sw.get_indir(IMG_RUN_FILES[step]) 
        #bg_fn = sw.get_outdir(step+'-BACKGROUND.fits')
        #img_bg_sub_fn = sw.get_indir(IMG_RUN_FILES[STEPS[step_num+1]])
        #imtools.bg_sub(img_fn, bg_fn, img_bg_sub_fn)
        #new_files.extend([sw.get_outdir(step+'.cat'), img_bg_sub_fn, bg_fn])
        #new_files.extend([sw.get_outdir(step+'.cat'), img_bg_sub_fn, bg_fn])
        del sw

    step_num = 1
    step = STEPS[step_num]
    do_step, config = pipe_steps[step]
    if do_step:
        sw = _start_sex(step, config, relpath)
        img_fn = sw.get_indir(IMG_RUN_FILES[step])
        seg_fn = sw.get_outdir(step+'-SEGMENTATION.fits')
        rms_fn = sw.get_outdir(STEPS[step_num-1]+'-BACKGROUND_RMS.fits')
        sky_fn = sw.get_outdir(STEPS[step_num-1]+'-BACKGROUND.fits')
        clean_img_fn = sw.get_indir(IMG_RUN_FILES[STEPS[step_num+1]])
        new_files.append(clean_img_fn)
        imtools.replace_with_sky(img_fn, seg_fn, rms_fn, sky_fn, write=clean_img_fn)
        new_files.append(sw.get_outdir(step+'.cat'))
        new_files.extend([sw.get_outdir(f) for f in \
                          sw.get_config()['CHECKIMAGE_NAME'].split(',')])
        del sw

    step_num = 2
    step = STEPS[step_num]
    do_step, config = pipe_steps[step]
    if do_step:
        sw = _start_sex(step, config, relpath)

    ###############################################
    # Make cuts on the final pipelie catalog
    ###############################################

    cat = sexpy.read_cat(sw.get_outdir(step+'.cat'))
    # cat = apply_cuts(cat)
    outfile = os.path.join(results_dir, run_label+'.cat')
    regfile = outfile[:-4]+'.reg'
    cat.write(outfile, format='ascii')

    if make_ds9reg:
        sexpy.cat_to_ds9reg(cat, outfile=regfile, **kwargs)
        new_files.append(regfile)
    if view_with_ds9:
        from toolbox.utils import ds9view
        final_step = STEPS[-1]
        ds9view(sw.get_indir(IMG_RUN_FILES[final_step]), regfile)

    if clean:
        new_files.remove(sw.get_outdir('clean.cat'))
        for f in new_files:
            print('deleting', f)
            os.remove(f)
    else:
        print('\ncreated files\n-------------')
        print('\n'.join(new_files))

    if log_fn is not None:
        # switch stdout back
        logfile.close()
        sys.stdout = stdout
