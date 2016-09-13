"""
Tools for mask making for photometry.
SEP is used extensively throughout: https://sep.readthedocs.io

The logic and structure of these functions were heavily inspired 
by Song Huang's work: https://github.com/dr-guangtou/hs_hsc/py
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy  as np
import scipy.ndimage as ndimage

import sep

__all__ = ['meas_back', 'detect_sources', 'hot_n_cold', 
           'make_seg_mask', 'make_obj_mask']


def _byteswap(arr):
    """
    If array is in big-endian byte order (as astropy.io.fits
    always returns), swap to little-endian for SEP.
    """
    if arr.dtype.byteorder is '>':
        arr = arr.byteswap().newbyteorder()
    return arr


def make_seg_mask(seg, grow_sig=6.0, mask_thresh=0.01, mask_max=1000.0):
    """
    Make mask from segmentation images. 

    Parameters
    ----------

    Returns
    -------
    """
    mask = seg.copy()
    mask[mask>0] = mask_max
    mask = ndimage.gaussian_filter(mask, sigma=grow_sig)
    mask = mask > (mask_max*mask_thresh)
    return mask.astype(int)


def make_obj_mask(cat, img_shape, grow_r=1.0):
    """
    Use SEP to build a mask based on objects in input catalog.

    Parameters
    ----------

    Returns
    -------
    """
    mask = np.zeros(img_shape, dtype='uint8')
    sep.mask_ellipse(mask, cat['x'], cat['y'], cat['a'],
                     cat['b'], cat['theta'], grow_r)
    return mask


def meas_back(img, backsize, ffrac=0.5, mask=None, sub_from_img=True):
    """
    Measure the sky background of image.

    Parameters
    ----------
    img : ndarray
        2D numpy array of image.
    backsize : int
        Size of background boxes in pixels.
    backffrac : float, optional
        The fraction of background box size for the 
        filter size for smoothing the background.
    mask : ndarray, optional
        Mask array for pixels to exclude from background
        estimation. 
    sub_from_img : bool, optional
        If True, also return background subtracted image.

    Returns
    -------
    bkg : sep.Background object 
       See SEP documentation for methods & attributes. 
    img_bsub : ndarray, if sub_from_img is True
    """
    img = _byteswap(img)
    mask = mask if mask is None else mask.astype(bool)
    bw = bh = backsize
    fw = fh = int(backffrac*backsize)
    bkg = sep.Background(img, mask=mask,  bw=bw, bh=bh, fw=fw, fh=fh)
    if sub_from_img:
        bkg.subfrom(img)
        return bkg, img
    else:
        return bkg


def detect_sources(img, thresh, backsize, backffrac=0.5, sig=None, 
                   mask=None, return_all=False, **kwargs):
    """
    Detect sources to construct a mask for photometry. 

    Parameters
    ----------

    Returns
    -------
    obj : 
    seg : 
    """
    img = _byteswap(img)
    bkg, img = meas_back(img, backsize, backffrac, mask)
    if sig is None:
        thresh *= bkg.globalrms
    else:
        sig = _byteswap(sig)
    obj, seg = sep.extract(img, thresh, err=sig, 
                           segmentation_map=True, **kwargs)

    return (obj, seg, bkg, img) if return_all else (obj, seg)
