
"""
Some functions to manipulate fits files.
"""

from __future__ import print_function

__all__ = ['sig_to_wts', 'wts_with_badpix', 'prep_for_sex']

import os
from astropy.io import fits

def _get_sexpath(flow):
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

def sig_to_wts(sigfile, wfile='wts.fits', sexpath=True):
    """
    Convert sigma image to weights image, where 
    weight = 1/sigma**2. 

    Parameters
    ----------
    sigfile : string
        The input sigma image file.
    wfile : string, optional
        The output weights image file.
    sexpath : bool, optional
        It True, will assume files are in
        and to be saved in sextractor in/out 
        directories. If False, assume desired 
        path is given in the file names.
    """
    if sexpath:
        sigfile = os.path.join(_get_sexpath('in'), sigfile)
        wfile = os.path.join(_get_sexpath('in'), wfile)
    sigfits = fits.open(sigfile)[0]
    weights = 1.0/sigfits.data**2
    print('writing', wfile)
    fits.writeto(wfile, weights, sigfits.header, clobber=True)

def wts_with_badpix(wfile, badfile, wnewfile='wts_bad.fits', 
                    flagval=-100.0, sexpath=True):
    """
    Flag bad pixels in the weight image for sextractor.

    Parameters
    ----------
    badfile : string
        Input bad pixel map file (0 = good pixels).
    wfile : string
        Input weight image file (weight = 1/sigma**2).
    wnewfile : string, optional
        Output weights + badpix file.
    flagval : float, optional
        The weight to be assigned to bad pixels.
        (sextractor default threshhold = 0)
    sexpath : bool, optional
        It True, will assume files are in
        and to be saved in sextractor in/out 
        directories. If False, assume desired 
        path is given in the file names.

    Notes
    -----
    The new weight file will be written to the same
    directory as badfile and wfile.
    """
    if sexpath:
        badfile = os.path.join(_get_sexpath('in'), badfile)
        wfile = os.path.join(_get_sexpath('in'), wfile)
    wnewfile = os.path.join(os.path.dirname(wfile), wnewfile)
    badpix = fits.getdata(badfile)
    wfits = fits.open(wfile)[0]
    wfits.data[badpix!=0] = flagval
    print('writing', wnewfile)
    fits.writeto(wnewfile, wfits.data, wfits.header, clobber=True)

def prep_for_sex(tract, patch, band='I'):
    """
    Prep fits files for sextractor.

    Parameters
    ----------
    tract : string
        HSC tract. 
    patch : string
        HSC patch
    band : string, optional
        HSC filter (GRIZY). 

    Notes
    -----
    Assumes the following file structure:
    {sextractor in/out dirs}/HSC-band/tract/patch
    """
    patch_label = patch[0]+'-'+patch[-1]
    path = 'HSC-'+band.upper()+'/'+str(tract)+'/'+patch_label+'/'
    sigfile = path+'sig.fits'
    badfile = path+'bad.fits'
    wfile = path+'wts.fits'
    sig_to_wts(sigfile, wfile, sexpath=True)
    wts_with_badpix(wfile, badfile, sexpath=True)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='prep fits files for sextractor.')
    parser.add_argument('tract', type=int, help='tract of observation')
    parser.add_argument('patch', type=str, help='patch of observation')
    parser.add_argument('-b', '--band', help='observation band', default='I')
    args = parser.parse_args()
    prep_for_sex(args.tract, args.patch, args.band)
