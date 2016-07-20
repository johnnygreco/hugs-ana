
"""
Some functions to manipulate fits files.
"""

from __future__ import print_function

__all__ = ['sig_to_weight']

import os
from astropy.io import fits

def _get_path(flow):
    """
    Private function to get sexin or sexout path.
    
    Parameters
    ----------
    flow : string
        'in' or 'out' directory.

    Returns
    -------
    path : sring
        The desired path.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(path)
    path = os.path.join(path, 'sex'+flow)
    assert os.path.isdir(path), path+' does not exist'
    return path

def sig_to_wts(sigfile, wfile='wts.fits'):
    """
    Convert sigma image to weights image, where 
    weight = 1/sigma**2. 

    Parameters
    ----------
    sigfile : string
        The input sigma image file.
    wfile : string, optional
        The output weights image file.

    Notes
    -----
    The weights file will be written to the same 
    directory as sigfile, which should be within 
    the sexin directory. 
    """
    sigfile = os.path.join(_get_path('in'), sigfile)
    wfile = os.path.join(os.path.dirname(sigfile), wfile)
    sigfits = fits.open(sigfile)[0]
    weights = 1.0/sigfits.data**2
    print('writing', wfile)
    fits.writeto(wfile, weights, sigfits.header, clobber=True)

def wts_with_badpix(badfile, wfile, wnewfile='wts_bad.fits', flagval=-100.0):
    """
    Flag bad pixels in the weight image for sextractor.

    Parameters
    ----------
    badfile : string
        Input band pixel map file (0 = good pixels).
    wfile : string
        Input weight image file (weight = 1/sigma**2).
    wnewfile : string, optional
        Output weights + badpix file.
    flagval : float, optional
        The weight to be assigned to bad pixels.

    Notes
    -----
    The new weight file will be written to the same
    directory as badfile and wfile, which should be 
    within the sexin directory.
    """
    badfile = os.path.join(_get_path('in'), badfile)
    wfile = os.path.join(_get_path('in'), wfile)
    wnewfile = os.path.join(os.path.dirname(wfile), wnewfile)
    badpix = fits.getdata(badfile)
    wfits = fits.open(wfile)[0]
    wfits.data[badpix!=0] = flagval
    print('writing', wnewfile)
    fits.writeto(wnewfile, wfits.data, wfits.header, clobber=True)

if __name__=='__main__':
    badfile = 'deepCoadds/HSC-I/9616/0-3/bad.fits'
    wfile = 'deepCoadds/HSC-I/9616/0-3/wts.fits'
    wts_with_badpix(badfile, wfile)
