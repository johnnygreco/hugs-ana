
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
    import argparse
    from astropy.io import fits
    parser = argparse.ArgumentParser(description='Get cutout of fits image')
    parser.add_argument('file', type=str, help='file name')
    parser.add_argument('ra', type=float, help='central ra of cutout')
    parser.add_argument('dec', type=float, help='central dec of cutout')
    parser.add_argument('-s', '--size', help='size of cutout', default=300)
    parser.add_argument('-w', '--write', help='save file name', default=None)
    args = parser.parse_args()
    f = fits.open(args.file)[0]
    cutout = get_cutout(f.data, args.ra, args.dec, f.header, size=args.size, save_fn=args.write)
    if args.write is None:
        import matplotlib.pyplot as plt
        from toolbox.image import zscale
        vmin, vmax = zscale(cutout.data)
        plt.imshow(cutout.data, vmin=vmin, vmax=vmax, cmap=plt.cm.cubehelix_r)
        try: import RaiseWindow
        except: pass
        plt.show()
