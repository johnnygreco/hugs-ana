import numpy as np
from astropy.io import fits

__all__=['gen_sky_noise', 'replace_with_sky']

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
        header = fits.getheader(rms_file)
        fits.writeto(write, noise, header, clobber=True)
    else:
        return noise

def replace_with_sky(img_file, seg_file, rms_file, sky_file=None, write=None): 
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

    Returns
    -------
    img.data : ndarray, if write=None
        The new image array with the given patches replaced with sky.
    """
    noise = gen_sky_noise(rms_file, sky_file)
    img = fits.open(img_file)[0]
    seg_map = fits.getdata(seg_file)
    img.data[seg_map!=0] = noise[seg_map!=0]
    if write is not None:
        fits.writeto(write, img.data, img.header, clobber=True)
    else:
        return img.data
