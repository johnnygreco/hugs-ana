"""
A collection of functions for manipulating fits images. 
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from astropy.io import fits

__all__=['open_me_fits', 'bg_sub', 'gen_sky_noise', 'replace_with_sky']

def open_me_fits(fn):
    """
    Open a multi-extension fits file, where we assume the structure is
    f[0], f[1], f[2], f[3] = header, image, mask, variance. 

    Parameters
    ----------
    fn : string
        Fits file name.

    Returns
    -------
    img, mask, var : ndarray
        The image, mask, and variance images.
    img_head : fits header
        The header associated with the image.
    """
    hdulist = fits.open(fn)
    img, mask, var = hdulist[1].data, hdulist[2].data, hdulist[3].data
    img_head = hdulist[1].header
    return img, mask, var, img_head

def bg_sub(img_file, bg_file, write=None):
    """
    Subtract sky background from image. 

    Parameters
    ----------
    img_file : string
        Fits file containing the orginal image.
    bg_file : string
        Fits file containing the sky background.
    write : string, optional
        If not None, the file name to write the 
        bg subtracted image to. 

    Returns
    -------
    img_bg_sub : ndarray, if write=None
        The bg subtracted image
    """
    img = fits.open(img_file)[0]
    bg = fits.getdata(bg_file)
    img_bg_sub = img.data - bg
    if write is None:
        return img_bg_sub
    else:
        assert (img_file is not write) and (bg_file is not write)
        assert write[-8:] not in ['img.fits', 'wts.fits']
        print('writing', write)
        fits.writeto(write, img_bg_sub, img.header, clobber=True)

def gen_sky_noise(rms_file, sky_file=None, write=None):
    """
    Generate (Gaussian) sky noise given a map of the rms sky level.

    Parameters
    ----------
    rms_file : string
        Fits file that contains the rms sky level. 
    sky_file : string, optional
        Fits file that contains the sky level. If
        None, the rms level is centered at zero. 
    write : string, optional
       If not None, the file name to write the 
        noise to. 
        
    Returns
    -------
    noise : 2D ndarray, if write=None
        Gaussian sky noise. If sky is not 
        None, the mean of the noise will be 
        the sky level. 
    """
    rms = fits.getdata(rms_file)
    noise = rms*np.random.randn(rms.shape[0], rms.shape[1])
    if sky_file is not None:
        sky = fits.getdata(sky_file)
        noise += sky
    if write is not None:
        assert (rms_file is not write) and (rms_file is not write)
        assert write[-8:] not in ['img.fits', 'wts.fits']
        print('writing', write)
        header = fits.getheader(rms_file)
        fits.writeto(write, noise, header, clobber=True)
    else:
        return noise

def replace_with_sky(img_file, seg_file, rms_file, sky_file=None, write=None,
                     dilator=None): 
    """
    Replace patches of sky associated with objects with sky noise.

    Parameters
    ----------
    img_file : string
        Fits file of the original image, which will have patches 
        of sky replaced with sky noise. 
    seg_file : string
        Fits file that contains a segmentation map where any
        pixel that is not zero is associated with an object,
        which will be replaced with sky noise.
    rms_file : string
        Fits file that contains the rms sky level. 
    sky_file : string, optional
        Fits file that contains the sky level. If
        None, the rms level is centered at zero. 
    write : string, optional
        If not None, the file name to write new image to.
    dilator : int or ndarray, optional
        If type is int, the size of the square array used to dilate 
        the segmentation image. If type is ndarray, must be the 
        structuring element used for the dilation.

    Returns
    -------
    img.data : ndarray, if write=None
        The new image array with the given patches replaced with sky.
    """
    noise = gen_sky_noise(rms_file, sky_file)
    img = fits.open(img_file)[0]
    seg_map = fits.getdata(seg_file)
    if dilator is not None:
        from scipy import ndimage
        print('performing binary dilation on segmentation image...')
        if type(dilator) is int:
            dilator = np.ones((dilator, dilator))
        else:
            assert type(dilator) is np.ndarray, 'not a valid structuring element'
        seg_map = (seg_map!=0)
        seg_map = ndimage.binary_dilation(seg_map, dilator)
    img.data[seg_map!=0] = noise[seg_map!=0]
    if write is not None:
        for fn in [img_file, seg_file, rms_file, sky_file]:
            assert fn is not write
        assert write[-8:] not in ['img.fits', 'wts.fits']
        print('writing', write)
        fits.writeto(write, img.data, img.header, clobber=True)
    else:
        return img.data
