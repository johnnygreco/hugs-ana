#!/usr/bin/env python 

"""
Use hugs.phot to do basic photometry.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import numpy as np
from astropy.io import fits
import hugs

outdir = os.path.join(os.environ.get('DROP_DIR'), 
                      'projects/HugsOut/photometry')

def main(fn, thresh, backsize, gal_pos='center', visualize=False):
    try:
        img, mask, var, img_head = hugs.imtools.open_fits(fn)
        sig = np.sqrt(var) # not currently using sigma image
    except IndexError:
        print('Fits file not a multi-extension cube.')
        print('Continuing without an initial mask.')
        img, img_head = hugs.imtools.open_fits(fn, False)
        mask = None
        sig = None
    phot_mask = hugs.phot.make_phot_mask(
        img, thresh, backsize, gal_pos=gal_pos, mask=mask)
    if visualize:
        hugs.phot.viz.overlay_mask(img, phot_mask)
    
    # create masked image for ellipse
    img_ell = img.copy()
    img_ell[phot_mask>0] = np.nan
    img_ell_fn = os.path.join(outdir, 'img_masked_ell.fits')
    print('writing', img_ell_fn)
    fits.writeto(img_ell_fn, img_ell, img_head, clobber=True)


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Fits file name')
    parser.add_argument('--thresh', type=float, 
                        help='Detection threshold', default=1.5)
    parser.add_argument('--backsize', type=int, 
                        help='Background box size', default=100)
    parser.add_argument('--db_nthr', type=float, 
                        help='Deblending num thresholds', default=32)
    parser.add_argument('--db_cont', type=float, 
                        help='Deblending contrast', default=0.005)
    parser.add_argument('--viz', action='store_true',
                        help='Visualize results', default=False)
    parser.add_argument('--gal_pos', type=str, 
                        help='galaxy position', default='center')
    args = parser.parse_args()
    if args.gal_pos!='center':
        args.gal_pos = [float(p) for p in args.gal_pos.split(',')]
    main(args.file, args.thresh, args.backsize, visualize=args.viz, gal_pos=args.gal_pos)

