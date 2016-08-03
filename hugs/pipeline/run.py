from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
import numpy as np

import time
import sexpy
from .. import imtools
from ..apply_cuts import apply_cuts

__all__ = ['run']

IMG_RUN_FILES = {'bright' : 'img.fits', 
                 'assoc'  : 'img_bg_sub.fits', 
                 'clean'  : 'img_bg_sub_clean.fits'}

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

    for do_step, step, config in pipe_steps:

        if do_step: 
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

            ###############################################
            # Perform step-specific tasks, which will are 
            # necessary for the next step
            ###############################################

            if step is 'bright':
                # subtract the bg from image
                img_fn = sw.get_indir('img.fits') 
                bg_fn = sw.get_outdir(step+'-BACKGROUND.fits')
                img_bg_sub_fn = sw.get_indir('img_bg_sub.fits')
                new_files.append(img_bg_sub_fn)
                imtools.bg_sub(img_fn, bg_fn, img_bg_sub_fn)
                new_files.append(sw.get_outdir(step+'.cat'))
            elif step is 'assoc':
                # make "clean" image with sky replacing bright sources
                img_fn = sw.get_indir('img_bg_sub.fits') 
                seg_fn = sw.get_outdir('assoc-SEGMENTATION.fits')
                rms_fn = sw.get_outdir('bright-BACKGROUND_RMS.fits')
                clean_img_fn = sw.get_indir('img_bg_sub_clean.fits')
                new_files.append(clean_img_fn)
                imtools.replace_with_sky(img_fn, seg_fn, rms_fn, write=clean_img_fn)
                new_files.append(sw.get_outdir(step+'.cat'))

            # remember new files
            new_files.extend([sw.get_outdir(f) for f in \
                              sw.get_config()['CHECKIMAGE_NAME'].split(',')])

    ###############################################
    # Make cuts on the final pipelie catalog
    ###############################################

    cat = sexpy.read_cat(sw.get_outdir(step+'.cat'))
    cat = apply_cuts(cat)
    outfile = os.path.join(results_dir, run_label+'.cat')
    regfile = outfile[:-4]+'reg'
    cat.write(outfile, format='ascii')

    if make_ds9reg:
        sexpy.cat_to_ds9reg(cat, outfile=regfil, **kwargs)
        new_files.append(regfile)
    if view_with_ds9:
        from toolbox.utils import ds9view
        final_step = pipe_steps[-1][1]
        ds9view(sw.get_indir(IMG_RUN_FILES[final_step]), regfile)

    if clean:
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
