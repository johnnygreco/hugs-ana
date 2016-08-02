
from __future__ import print_function

import numpy as np

__all__ = ['rmedian']

def _ring(r_inner, r_outer, dtype=np.int, invert=False):
    """
    Generate a 2D ring footprint.

    Paramters
    ---------
    r_inner : int
        The inner radius of ring in pixels.
    r_outer : int
        The outer radius of ring in pixels.
    dtype : data type, optional
        The data type of the output array
    invert : bool, optional
        If True, invert the ring kernal (i.e., 1 <--> 0).

    Returns
    -------
    fp : 2D ndarray
        The ring footprint with 1's in the 
        annulus and 0's everywhere else.
    """
    assert r_outer >= r_inner, 'must have r_outer >= r_inner'
    x = np.arange(-int(r_outer), int(r_outer)+1)
    r = np.sqrt(x**2 + x[:,None]**2)
    annulus = (r>r_inner) & (r<=r_outer)
    if invert:
        annulus = ~annulus
    r[annulus] = 1
    r[~annulus] = 0
    fp = r.astype(dtype)
    return fp

def rmedian(infile, outfile, r_inner, r_outer, **kwargs):
    """
    Median filter image with a ring footprint. This
    is similar to the rmedian iraf task; although, for 
    reasons I do not understand, the results are somewhat 
    different. 

    Parameters
    ----------
    infile : string
        The input fits file. 
    outfile : string
        The output fits file.
    r_inner : int
        The inner radius of the ring in pixels.
    r_outer : int
        The outer radius of the ring in pixels.
    """
    from astropy.io import fits
    from scipy.ndimage import median_filter

    infits = fits.open(infile)[0]
    fp = _ring(r_inner, r_outer, **kwargs)
    print('applying ring filer to', infile)
    filtered = median_filter(infits.data, footprint=fp)
    print('writing', outfile)
    fits.writeto(outfile, filtered, infits.header, clobber=True)
