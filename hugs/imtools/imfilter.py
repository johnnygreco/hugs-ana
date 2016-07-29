
from __future__ import print_function

__all__ = ['rmedian']

def rmedian(infile, outfile, r_inner, r_outer):
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
    from footprints import ring
    from astropy.io import fits
    from scipy.ndimage import median_filter

    infits = fits.open(infile)[0]
    fp = ring(r_inner, r_outer)
    print('filtering', infile)
    filtered = median_filter(infits.data, footprint=fp)
    print('writing', outfile)
    fits.writeto(outfile, filtered, infits.header, clobber=True)
