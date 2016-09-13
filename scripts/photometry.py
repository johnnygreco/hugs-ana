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
        img_head, img, mask, var = hugs.imtools.open_fits(fn)
        sig = np.sqrt(var) # not currently using sigma image
    except IndexError:
        print('Fits file not a multi-extension cube.')
        print('Continuing without an initial mask.')
        img_head, img = hugs.imtools.open_fits(fn, False)
        mask = None
        sig = None
    img0 = img.copy()

    params = {'deblend_nthresh': 16, 'deblend_cont': 0.001, 'minarea': 5}
    phot_mask = hugs.phot.make_phot_mask(
        img, thresh, backsize, gal_pos=gal_pos, mask=mask, grow_obj=3.,
        grow_sig=6, mask_thresh=0.02, obj_rmin=20, sep_extract_params=params)
    assert np.allclose(img0, img)
    if visualize:
        hugs.phot.viz.overlay_mask(img, phot_mask)

    fits.writeto('/Users/protostar/Desktop/test_imfit/mask.fits', phot_mask, img_head, clobber=True)




if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Fits file name')
    parser.add_argument('--thresh', type=float, 
                        help='Mask detection threshold', default=1.5)
    parser.add_argument('--backsize', type=int, 
                        help='Mask background box size', default=100)
    parser.add_argument('--db_nthr', type=float, 
                        help='Mask deblending num thresholds', default=32)
    parser.add_argument('--db_cont', type=float, 
                        help='Mask deblending contrast', default=0.005)
    parser.add_argument('--viz', action='store_true',
                        help='Visualize results', default=False)
    parser.add_argument('--gal_pos', type=str, 
                        help='galaxy position', default='center')
    args = parser.parse_args()
    if args.gal_pos!='center':
        args.gal_pos = [float(p) for p in args.gal_pos.split(',')]
    main(args.file, args.thresh, args.backsize, args.gal_pos, args.viz)
