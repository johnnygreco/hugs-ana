"""
Tools for mask making for photometry.
SEP is used extensively throughout: https://sep.readthedocs.io

The logic and structure of these functions were heavily inspired 
by Song Huang's work: https://github.com/dr-guangtou/hs_hsc/py
"""

import numpy  as np
import scipy.ndimage as ndimage

import sep

__all__ = ['meas_back', 'detect_sources', 'hot_n_cold', 
           'seg_mask', 'obj_mask']


def _byteswap(arr):
    """
    If array is in big-endian byte order (as astropy.io.fits
    always returns), swap to little-endian for SEP.
    """
    if arr.dtype.byteorder is '>':
        arr = arr.byteswap().newbyteorder()
    return arr


def seg_mask(seg, grow_sig=6.0, mask_thresh=0.01, mask_max=1000.0):
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


def obj_mask(cat, img_shape, grow_r=1.0):
    """
    Use SEP to build a mask based on objects input catalog.

    Parameters
    ----------

    Returns
    -------
    """
    mask = np.zeros(img_shape, dtype='uint8')
    sep.mask_ellipse(mask, cat['x'], cat['y'], cat['a'],
                     cat['b'], cat['theta'], grow_r)
    return mask


def meas_back(img, size, ffrac=0.5, mask=None, sub_from_img=True):
    """
    Measure the sky background of image.

    Parameters
    ----------
    img : ndarray
        2D numpy array of image.
    size : int
        Size of background boxes in pixels.
    ffrac : float, optional
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
    bw = bh = size
    fw = fh = int(ffrac*size)
    bkg = sep.Background(img, mask=mask,  bw=bw, bh=bh, fw=fw, fh=fh)
    if sub_from_img:
        bkg.subfrom(img)
        return bkg, img
    else:
        return bkg


def detect_sources(img, thresh, backsize, backffrac=0.5, sig=None, 
                   mask=None, minarea=5, kern='default', ftype='matched', 
                   db_nthr=32, db_cont=0.005, clean=True, 
                   clean_param=1.0, return_all=False):
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
    if kern is 'default':
        kern = sep.default_kernel
    obj, seg = sep.extract(
        img, thresh, err=sig, filter_kernel=kern, filter_type=ftype, 
        segmentation_map=True, clean=True, clean_param=1.0, 
        deblend_cont=db_cont, deblend_nthresh=db_nthr)
    return (obj, seg, bkg, img) if return_all else (obj, seg)


def _combine_cats(hot, cold, tol=6.0, keepH=True):
    """
    Combine catalogs from hot and cold runs.

    Parameters
    ----------

    Returns
    -------

    Notes
    ----
    This function was written by Song Huang.
    """
    objC = cold.copy()
    objH = hot.copy()
    # The central coordinates of each objects
    objCX = objC['xpeak']
    objCY = objC['ypeak']
    objHX = objH['xpeak']
    objHY = objH['ypeak']
    # Get the minimum separation between each Hot run object and all the
    # Cold run objects
    minDistH = np.asarray(list(map(lambda x, y: np.min(np.sqrt((x - objCX)**2.0 +
                          (y - objCY)**2.0)), objHX, objHY)))
    minDistC = np.asarray(list(map(lambda x, y: np.min(np.sqrt((x - objHX)**2.0 +
                          (y - objHY)**2.0)), objCX, objCY)))
    # Locate the matched objects
    indMatchH = np.where(minDistH < tol)
    indMatchC = np.where(minDistC < tol)
    # Delete the matched objects from the Hot run list
    objHnew = objH.copy()
    objHnew = np.delete(objHnew, indMatchH)
    objCnew = objC.copy()
    objCnew = np.delete(objCnew, indMatchC)

    # Try to account for the difference in size and area of the same
    # object from Cold and Hot run
    objMatchH = objH[(minDistH < tol) & (np.log10(objH['npix']) < 2.6)]
    objMatchC = objC[(minDistC < tol) & (np.log10(objC['npix']) < 2.6)]
    # This is designed to be only a rough match
    # Only works for not very big galaxies, will fail for stars
    aRatio = (np.nanmedian(objMatchC['a']) /
              np.nanmedian(objMatchH['a']))
    objHnew['a'] *= aRatio
    objHnew['b'] *= aRatio
    objH['a'] *= aRatio
    objH['b'] *= aRatio

    nRatio = (np.nanmedian(objMatchC['npix']) /
              np.nanmedian(objMatchH['npix']))
    objHnew['npix'] = objHnew['npix'] * nRatio
    objH['npix'] = objH['npix'] * nRatio
    if keepH:
        objComb = np.concatenate((objH, objCnew))
    else:
        objComb = np.concatenate((objC, objHnew))
    return objComb


def hot_n_cold(img, tholds, bsizes, ntholds, contrasts, backffrac=0.5, 
               sig=None, mask=None, minarea=5, kern='default', ftype='matched', 
               clean=True, clean_param=1.0, tol=6, keep_hot=False, 
               return_all=False):
    """
    Detect sources using old school technique of hot and cold runs.

    hot  --> small background size, higher detection threshold, 
             less aggressive deblending
    cold --> large background size, low detection threshold, 
             aggressive deblending

    Parameters
    ----------

    Returns
    -------
    """

    # hot run
    imgH = img.copy()
    backsize = bsizes[0]
    thresh = tholds[0]
    db_nthr = ntholds[0]
    db_cont = contrasts[0]
    objH, segH, bkgH, imgH = detect_sources(
        imgH, thresh, backsize, backffrac=backffrac, sig=sig, mask=mask, 
        minarea=minarea, kern=kern, ftype=ftype, db_nthr=db_nthr, 
        db_cont=db_cont, clean=clean, clean_param=clean_param, return_all=True)

    # cold run
    imgC = img.copy()
    backsize = bsizes[1]
    thresh = tholds[1]
    db_nthr = ntholds[1]
    db_cont = contrasts[1]
    objC, segC, bkgC, imgC = detect_sources(
        imgC, thresh, backsize, backffrac=backffrac, sig=sig, mask=mask, 
        minarea=minarea, kern=kern, ftype=ftype, db_nthr=db_nthr, 
        db_cont=db_cont, clean=clean, clean_param=clean_param, return_all=True)

    cat_final = _combine_cats(objH, objC, tol, keep_hot)

    return (cat_final, segH, segC, 
            objH, objC, bkgH, bkgC) if return_all else (cat_final, segH, segC)
