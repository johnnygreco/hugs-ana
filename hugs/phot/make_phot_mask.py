
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .mask_utils import *
from .._utils import bit_flag_dict

def _outside_circle(cat, xc, yc, r):
    return np.sqrt((cat['x']-xc)**2 + (cat['y']-yc)**2) > r

def make_phot_mask(img, thresh, backsize, backffrac=0.5, sig=None, mask=None, 
              minarea=5, kern='default', ftype='matched', db_nthr=32, 
              db_cont=0.005, clean=True, clean_param=1.0, gal_pos='center', 
              seg_rmin=100.0, obj_rmin=15.0, grow_sig=5.0, mask_thresh=0.01, 
              grow_obj=4.5):
    """
    Parameters
    ----------

    Returns
    -------
    """

    if gal_pos=='center':
        gal_x, gal_y = (img.shape[1]/2, img.shape[0]/2)
    else:
        gal_x, gal_y = gal_pos

    #################################################################
    # If an HSC mask is given, use the non-detection bits as a bad 
    # pixel map. 
    #################################################################

    if mask is not None:
        hsc_bad_mask = mask.copy()
        detected = bit_flag_dict['DETECTED']
        hsc_bad_mask[hsc_bad_mask==detected] = 0
    else:
        hsc_bad_mask = np.zeros(img.shape, dtype=int)
    
    #################################################################
    # Detect sources in image to mask before we do photometry.
    #################################################################

    obj, seg, bkg, img = detect_sources(
        img, thresh, backsize, backffrac, sig, mask, minarea, kern, 
        ftype, db_nthr, db_cont, clean, clean_param, True)

    #################################################################
    # Exclude objects inside seg_rmin and obj_rmin. Note that the 
    # segmentation label of the object at index i is i+1.
    #################################################################

    exclude_labels = np.where(~_outside_circle(obj, gal_x, gal_y, seg_rmin))[0] + 1
    for label in exclude_labels:
        seg[seg==label] = 0

    keepers = _outside_circle(obj, gal_x, gal_y, obj_rmin)
    obj = obj[keepers]

    #################################################################
    # Generate segmentation and object masks. Combine with HSC bad 
    # pixel mask (if given) to form the final mask.
    #################################################################
    
    seg_mask = make_seg_mask(seg, grow_sig, mask_thresh)
    obj_mask = make_obj_mask(obj, img.shape, grow_obj)
    final_mask = (seg_mask | obj_mask | hsc_bad_mask).astype(int)

    return final_mask
