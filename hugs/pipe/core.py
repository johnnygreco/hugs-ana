from __future__ import divison, print_function


import lsst.afw.detection as afwDetect

__all__ = ['thresh_type', 'get_psf_sigma', 'image_threshold']


def get_psf_sigma(exposure):
    """
    Get sigma of point-spread function.

    Parameters
    ----------
    exposure : lsst.afw.image.imageLib.ExposureF
        Exposure object. 

    Returns
    -------
    sigma : float
        Approximate standard deviation of the PSF
        of the image in this exposure.
    """
    psf = exposure.getPsf()
    sigma = psf.computeShape().getDeterminantRadius()
    return sigma


def image_threshold(masked_image, thresh, thresh_type='stdev', npix=1, 
                    rgrow=None, isogrow=False, plane_name='DETECTED', 
                    clear_mask=True):
    """
    Image thresholding. As bit mask will be set with name 'plane_name'.

    Parameters
    ----------
    masked_image : lsst.afw.image.imageLib.MaskedImageF
        A masked image object.
    thresh : float
        Threshold value.
    thresh_type : string, optional
        Threshold type: stdev, pixel_stdev, bitmask, value,
        or variace.
    npix : int, optional
        Minimum number of touching pixels in an object.
    rgrow : int, optional
        Number of pixels to grow footprints.
    isogrow : bool, optional
        If True, use (expensive) isotropic grow. 
    plane_name : string, optional
        Name of bit plane.
    clear_plane : bool, optional
        If True, clear the bit plane before thresholding

    Returns
    -------
    fp : lsst.afw.detection.detectionLib.FootprintSet
        Footprints assoicated with detected objects.
    """
    mask = masked_image.getMask()
    if clear_mask:
        mask.clearMaskPlane(mask.getMaskPlane(mask_name))
    thresh_type = getattr(afwDetect.Threshold, thresh_type.upper())
    thresh = afwDetect.Threshold(thresh, thresh_type)
    fp = afwDetect.FootprintSet(masked_image, thresh, mask_name, npix)
    if ngrow is not None:
        fp = afwDetect.FootprintSet(fp, rgrow, isogrow)
    fp.setMask(mask, mask_name)
    return fp


def run():
