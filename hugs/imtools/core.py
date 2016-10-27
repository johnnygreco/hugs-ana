from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from astropy.io import fits

__all__=['open_fits']

def open_fits(fn, muilti_ext=True):
    """
    Get data from fits file. If a multi-extension fits file, 
    we assume the structure is f[0], f[1], f[2], f[3] = header, 
    image, mask, variance. 
    Parameters
    ----------
    fn : string
        Fits file name.
    Returns
    -------
    img, mask, var : ndarray
        The image, mask, and variance images.
    img_head : fits header
        The header associated with the image.
    """
    hdulist = fits.open(fn)
    if muilti_ext:
        img, mask, var = hdulist[1].data, hdulist[2].data, hdulist[3].data
        img_head = hdulist[1].header
    else:
        img = hdulist[0].data
        img_head = hdulist[0].header
    return (img_head, img, mask, var) if muilti_ext else (img_head, img)

