from __future__ import divison, print_function

import numpy as np

import lsst.afw.detection as afwDetect

__all__ = ['get_psf_sigma', 'associate', 'image_threshold']


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


def associate(mask, fpset, radius=10, plane_name='THRESH_HIGH'):
    """
    Associate footprints in fpset with footprints in mask plane 
    'plane_name'. A footprint is associated with an object if 
    its center is within 'radius' pixels from an on bit in this 
    plane.

    Parameters
    ----------
    mask : lsst.afw.image.imageLib.MaskU
        Mask object with plane named 'plane_name'.
    fpset : lsst.afw.detection.detectionLib.FootprintSet
        Set of footprints to associate with objects in mask.
    radius : float
        Radius of association (in pixels) from the center of each
        footprint in fpset.
    plane_name : string
        Name of the bit plane in mask to associate footprints with. 

    Returns
    -------
    seg_assoc : 2D ndarray
        Segmentation image with non-zero values for all footprints 
        that are associated with an object in the mask. 

    Notes
    -----
    seg_assoc also includes footprints near objects with the 
    'BRIGHT_OBJECT' bit set.
    """
    from skimage.draw import circle 

    xy0 = mask.getXY0()
    bit_assoc = mask.getPlaneBitMask(plane_name)
    bit_bright = mask.getPlaneBitMask('BRIGHT_OBJECT')
    bit_vals = 2**np.arange(mask.getNumPlanesUsed())
    # False --> use footprint ids
    seg_assoc = fpset.insertIntoImage(False).getArray().copy() 
    for foot in fpset.getFootprints():
        peaks = np.array([p.getCentroid()-xy0 for p in foot.getPeaks()])
        xc, yc = peaks.mean(axis=0)
        rows, cols = circle(yc, xc, radius, shape=mask.getArray().shape)
        circ_pix = mask.getArray()[rows, cols]
        on_bits = [(bit_assoc in bit_vals[(b & bit_vals)!=0]) or\
                   (bit_bright in bit_vals[(b & bit_vals)!=0]) for b in circ_pix]
        if np.sum(on_bits)==0:
            seg_assoc[seg_assoc==foot.getId()] = 0
    return seg_assoc


def image_threshold(masked_image, thresh, thresh_type='stdev', npix=1, 
                    rgrow=None, isogrow=False, plane_name='', clear_mask=True):
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
    clear_mask : bool, optional
        If True, clear the bit plane before thresholding

    Returns
    -------
    fp : lsst.afw.detection.detectionLib.FootprintSet
        Footprints assoicated with detected objects.
    """
    mask = masked_image.getMask()
    thresh_type = getattr(afwDetect.Threshold, thresh_type.upper())
    thresh = afwDetect.Threshold(thresh, thresh_type)
    fp = afwDetect.FootprintSet(masked_image, thresh, npix)
    if rgrow is not None:
        fp = afwDetect.FootprintSet(fp, rgrow, isogrow)
    if plane_name:
        if clear_mask:
            mask.clearMaskPlane(mask.getMaskPlane(plane_name))
        mask.addMaskPlane(plane_name)
        fp.setMask(mask, plane_name)
    return fp


def run():
