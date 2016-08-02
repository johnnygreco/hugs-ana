
from __future__ import print_function

__all__  = ['cutout']

def cutout(data, coord, header=None, size=300, write=None):
    """
    Generate a postage stamp from from a fits image.

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

if __name__=='__main__':
    import argparse
    from astropy.io import fits
    parser = argparse.ArgumentParser(description='Get cutout of fits image')
    parser.add_argument('file', type=str, help='file name')
    parser.add_argument('x', type=float, help='central x (ra or pixel) coordinate of cutout')
    parser.add_argument('y', type=float, help='central y (dec or pixel) coordinate of cutout')
    parser.add_argument('-s', '--size', help='size of cutout', default=300)
    parser.add_argument('-w', '--write', help='save file name', default=None)
    parser.add_argument('--no_header', help='no header for WCS', action='store_true')
    args = parser.parse_args()
    f = fits.open(args.file)[0]
    header = None if args.no_header else f.header
    coord = (args.x, args.y)
    cutout = get_cutout(f.data, coord, header, size=args.size, write=args.write)
    if args.write is None:
        import matplotlib.pyplot as plt
        from toolbox.image import zscale
        vmin, vmax = zscale(cutout.data)
        plt.imshow(cutout.data, vmin=vmin, vmax=vmax, cmap=plt.cm.cubehelix_r, origin='lower')
        try: import RaiseWindow
        except: pass
        plt.show()
