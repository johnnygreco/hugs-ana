
from __future__ import print_function

__all__  = ['get_cutout']

def get_cutout(data, ra, dec, header, size=300, save_fn=None):
    """
    Generate a postage stamp from from a fits image.

    Parameters
    ----------
    data : 2D ndarray
        The data from the fits file.
    ra, dec : float
        The central coordinates for the cutout. 
    header : Fits header
        The fits header, which must have WCS info.
    size : int, array-like, optional
        The size of the cutout array along each axis.
        If an integer is given, will get a square. 
    save_fn : string, optional
        If not None, save the cutout to this 
        file name.

    Returns
    -------
    cutout : Cutout2D object, if save_fn is None
       A cutout object containing the 2D cutout data 
       array and the updated WCS.
    """
    from astropy.nddata import Cutout2D
    from astropy.coordinates import SkyCoord

    if header is not None:
        from astropy import wcs
        w = wcs.WCS(header)
    else:
        w = None

    coord = SkyCoord(ra, dec, unit="deg") 
    cutout = Cutout2D(data, coord, size, wcs=w)

    if save_fn is None:
        return cutout
    else:
        from astropy.io import fits
        header = cutout.wcs.to_header()
        fits.writeto(save_fn, cutout.data, header, clobber=True)

if __name__=='__main__':
    from astropy.io import fits
    file = '../sexin/group_3765/HSC-I_9347_1-8_img.fits'
    f = fits.open(file)[0]
    cutout = get_cutout(f.data, 179.78125, -0.0231389, 
                        f.header, size=300, save_fn='test.fits')
