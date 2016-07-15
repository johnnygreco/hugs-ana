from __future__ import division, print_function

import numpy as np

__all__ = ['write_kern', 'exp']

def write_kern(kern, fn, norm=True, comment=None, fmt='%.8g'):
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

    header = 'CONV NORM' if norm else 'CONV'
    if comment is not None:
        header += '\n'+comment

    outfile = os.path.join(outdir, fn)
    np.savetxt(outfile, kern, header=header, comments='', fmt=fmt)

def exp(size=9, alpha=5.0, write=False, **kwargs):
    """
    Generate 2D exponential kernal for sextractor.

    Parameters
    ----------
    size : odd int
        Number of pixel in x & y directions.
    alpha : float
        The scale length of the exponential.
    write : bool
        If True, call write_kern to write file 
        and return file name, else return the kernel.
    **kwargs : dict
        Inputs for write_kern

    Returns
    -------
    kern : 2D ndarray, if write=False
        The convolution kernel. 
    fn : string, if write=True
        The kernel file name.
    """
    assert size%2!=0, 'ERROR: size must be odd'

    x = np.arange(-int(size/2), int(size/2)+1)
    r = np.sqrt(x**2 + x[:,None]**2)
    kern = np.exp(-r/alpha)
    kern /= np.sum(kern)
    if write:
        fn = 'exp_{0}_{1}x{1}.conv'.format(alpha, size)
        comment = '# {0}x{0} convolution mask '.format(size)
        comment += 'of an exponential with alpha = {} pixels'.format(alpha)
        write_kern(kern, fn, comment=comment, **kwargs)
        return fn
    else:
        return kern
