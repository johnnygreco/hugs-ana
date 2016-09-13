
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .mask_utils import *
from .._utils import bit_flag_dict


def _outside_circle(cat, xc, yc, r):
    """
    Returns a mask of all objectes that fall outside a 
    circle centered at (xc, yc) of radius r. 
    """
    return np.sqrt((cat['x']-xc)**2 + (cat['y']-yc)**2) > r


def make_phot_mask(img, thresh, backsize, backffrac=0.5, sig=None, mask=None,
                   gal_pos='center', seg_rmin=100.0, obj_rmin=15.0, 
                   grow_sig=5.0, mask_thresh=0.01, grow_obj=4.5, 
                   mask_from_hsc=True, sep_extract_params={}):
    """
    Generate a mask for galaxy photometry using SEP. Many of these
    parameters are those of SEP, so see its documentation for 
    more info.

    Parameters
    ----------
    img : 2D ndarray
        Image to be masked.
    thresh : float
        Detection threshold for source extraction.  
    backsize : int
        Size of box for background estimation.
    backffrac : float, optional
        Fraction of backsize to make the background median filter.
    sig : 2D ndarray, optional
        Simga image. Must have same shape as img.
    mask : ndarray, optional
        Mask to apply before background estimation.
        Must have same shape as img.
    gal_pos : array-like, optional
        (x,y) position of galaxy in pixels. If 'center', the 
        center of the image is assumed.
    seg_rmin : float, optional
        Minimum radius with respect to gal_pos for the 
        segmentation mask. 
    obj_rmin : float, optional
        Minimum radius with respect to gal_pos for the 
        object mask. 
    grow_sig : float, optional
        Sigma of the Gaussian that the segmentation mask
        is convolved with to 'grow' the mask. 
    mask_thresh : float, optional
        All pixels above this threshold will be masked 
        in the seg mask. 
    grow_obj : float, optional
        Fraction to grow the objects of the obj mask. 
    mask_from_hsc : bool, optional
        If True, the input mask is from the HSC pipeline. 
    sep_extract_params : dict, optional
        Extra parameters for SEP's extract function. By extra, 
        we mean parameters that are not given as input to 
        this function. 
        
    Returns
    -------
    final_mask : 2D ndarray
        Final mask to apply to img, where 0 represents good pixels
        and 1 masked pixels. The final mask is a combination of 
        a segmentation, object, and (if given) HSC's bad pixel 
        mask. 
    """

    if gal_pos=='center':
        gal_x, gal_y = (img.shape[1]/2, img.shape[0]/2)
    else:
        gal_x, gal_y = gal_pos

    #################################################################
    # If an HSC mask is given, use the non-detection bits as a bad 
    # pixel map. 
    #################################################################

    if (mask is not None) and mask_from_hsc:
        hsc_bad_mask = mask.copy()
        detected = bit_flag_dict['DETECTED']
        hsc_bad_mask[hsc_bad_mask==detected] = 0
    else:
        hsc_bad_mask = np.zeros(img.shape, dtype=int)
    
    #################################################################
    # Detect sources in image to mask before we do photometry.
    #################################################################

    obj, seg, bkg, img = detect_sources(img, thresh, backsize, backffrac, sig, 
                                        mask, True, **sep_extract_params)

    #################################################################
    # Exclude objects inside seg_rmin and obj_rmin. Note that the 
    # segmentation label of the object at index i is i+1.
    #################################################################

    exclude_labels = np.where(~_outside_circle(obj, gal_x, gal_y, seg_rmin))[0] 
    exclude_labels += 1
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
