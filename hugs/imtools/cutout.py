from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__  = ['cutout']


def cutout(data, coord, header=None, size=301, write=None):
    """
    Generate a postage stamp from a fits image.

    Parameters
    ----------
    data : 2D ndarray
        The data from the fits file.
    coord : tuple
        The central coordinates for the cutout. If 
        header is None, then unit is pixels, else
        it is ra and dec in degrees.
    header : Fits header, optional
        The fits header, which must have WCS info.
    size : int, array-like, optional
        The size of the cutout array along each axis.
        If an integer is given, will get a square. 
    write : string, optional
        If not None, save the cutout to this 
        file name.

    Returns
    -------
    cutout : Cutout2D object, if write is None
       A cutout object containing the 2D cutout data 
       array and the updated WCS.
    """
    from astropy.nddata import Cutout2D
    from astropy.coordinates import SkyCoord

    if header is None:
        cutout = Cutout2D(data, coord, size)
    else:
        from astropy import wcs
        w = wcs.WCS(header)
        coord = SkyCoord(coord[0], coord[1], frame='icrs', unit="deg") 
        cutout = Cutout2D(data, coord, size, wcs=w)

    if write is None:
        return cutout
    else:
        from astropy.io import fits
        header = cutout.wcs.to_header() if header is not None else None
        fits.writeto(write, cutout.data, header, clobber=True)

