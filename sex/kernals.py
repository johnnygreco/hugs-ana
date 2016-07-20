from __future__ import division, print_function

__all__ = ['write_kern', 'exp', 'gauss']

import numpy as np

def write_kern(kern, fn, norm=True, comment=None, fmt='%.8f'):
    """
    Write convolution kernel file for sextractor.

    Parameters
    ----------
    kern : 2D ndarray
        The convolution kernel.
    fn : string
        Filename (convention: exp_5.0_9x9.conv).
    norm : bool, optional
        If True, kernel is to be normalized.
    comment : string, optional
        Comment for the convolution file.
    fmt : string, optional
        Numpy savetxt output format.
    """
    import os

    # must save in the runsex/config directory
    filedir = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(filedir, 'config')

    header = 'CONV NORM' if norm else 'CONV NONORM'
    if comment is not None:
        header += '\n'+comment

    outfile = os.path.join(outdir, fn)
    np.savetxt(outfile, kern, header=header, comments='', fmt=fmt)

def exp(size, alpha, norm_array=False, write=False, **kwargs):
    """
    Generate 2D, radially symmetric exponential kernal for sextractor, 
    produced by sampling at the midpoints of each pixel.

    Parameters
    ----------
    size : odd int
        Number of pixel in x & y directions.
    alpha : float
        The scale length of the exponential.
    norm_array : bool, optional
        If True, normalize the kern array. 
    write : bool, optional
        If True, call write_kern to write file 
        and return file name, else return the kernel.
    **kwargs : dict, optional
        Inputs for write_kern

    Returns
    -------
    kern : 2D ndarray, if write=False
        The convolution kernel. 
    fn : string, if write=True
        The kernel file name.

    Notes
    -----
    The kernel will be normalized by sextractor by 
    default, and the non-normalized files are a bit 
    cleaner due to less leading zeros. 
    """
    assert size%2!=0, 'ERROR: size must be odd'

    x = np.arange(-int(size/2), int(size/2)+1)
    r = np.sqrt(x**2 + x[:,None]**2)
    kern = np.exp(-r/alpha)
    if norm_array:
        kern /= kern.sum()
    
    if write:
        fn = 'exp_{0}_{1}x{1}.conv'.format(alpha, size)
        comment = '# {0}x{0} convolution mask '.format(size)
        comment += 'of an exponential with alpha = {} pixels'.format(alpha)
        write_kern(kern, fn, comment=comment, **kwargs)
        return fn
    else:
        return kern

def gauss(size, width, width_type='fwhm', norm_array=False, write=False, **kwargs):
    """
    Generate a 2D radially symmetric Gaussian kernel for sextractor,
    produced by sampling at the midpoints of each pixel.

    Parameters
    ----------
    size : odd int
        Number of pixel in x & y directions.
    width : float
        The width of the Gaussian. 
    width_type : string, optional
        The width type given ('fwhm' or 'sigma').
    norm_array : bool, optional
        If True, normalize the kern array. 
    write : bool, optional
        If True, call write_kern to write file 
        and return file name, else return the kernel.
    **kwargs : dict, optional
        Inputs for write_kern.

    Returns
    -------
    kern : 2D ndarray, if write=False
        The convolution kernel. 
    fn : string, if write=True
        The kernel file name.

    Notes
    -----
     i) The kernel will be normalized by sextractor by 
        default, and the non-normalized files are a bit 
        cleaner due to less leading zeros. 
    ii) I can't reporduce the sextractor default Gaussian 
        kernels. However, this function produces identical 
        results to astropy and wikipedia: 
        https://en.wikipedia.org/wiki/Gaussian_blur.
    """
    assert size%2!=0, 'ERROR: size must be odd'

    x = np.arange(-int(size/2), int(size/2)+1)
    r = np.sqrt(x**2 + x[:,None]**2)

    factor = 2.0*np.sqrt(2*np.log(2))
    if width_type=='fwhm':
        sigma = width/factor 
        fwhm = width
    elif width_type=='sigma':
        sigma = width
        fwhm = width*factor

    kern = np.exp(-r**2/(2*sigma**2))
    if norm_array:
        kern /= kern.sum()

    if write:
        fn = 'gauss_{0}_{1}x{1}.conv'.format(fwhm, size)
        comment = '# {0}x{0} convolution mask '.format(size)
        comment += 'of a Gaussian with fwhm = {} pixels'.format(fwhm)
        write_kern(kern, fn, comment=comment, **kwargs)
        return fn
    else:
        return kern
