#!/usr/bin/env python 

"""
Use hugs.phot to do basic photometry.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from astropy.io import fits
import hugs

def main(fn, thresh, backsize, visualize=True):
    img, mask, var, img_head = hugs.imtools.open_me_fits(fn)
    sig = np.sqrt(var) # not currently using sigma image
    phot_mask = hugs.phot.make_phot_mask(img, thresh, backsize, mask=mask)
    if visualize:
        hugs.phot.viz.overlay_mask(img, phot_mask)

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
    args = parser.parse_args()
    main(args.file, args.thresh, args.backsize)

