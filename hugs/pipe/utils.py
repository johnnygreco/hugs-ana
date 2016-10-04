from __future__ import division, print_function

import numpy as np


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
    # False --> use footprint ids
    seg_assoc = fpset.insertIntoImage(False).getArray().copy() 
    for foot in fpset.getFootprints():
        peaks = np.array([p.getCentroid()-xy0 for p in foot.getPeaks()])
        xc, yc = peaks.mean(axis=0)
        rows, cols = circle(yc, xc, radius, shape=mask.getArray().shape)
        circ_pix = mask.getArray()[rows, cols]
        on_bits = (circ_pix & mask.getPlaneBitMask(plane_name))!=0
        on_bits |= (circ_pix & mask.getPlaneBitMask('BRIGHT_OBJECT'))!=0
        if np.sum(on_bits)==0:
            seg_assoc[seg_assoc==foot.getId()] = 0
    return seg_assoc


def image_threshold(masked_image, thresh, thresh_type='stdev', npix=1, 
                    rgrow=None, isogrow=False, plane_name='', mask=None,
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
    mask : lsst.afw.image.imageLib.MaskU, optional
        Mask to set if not same as in masked_imaged
    clear_mask : bool, optional
        If True, clear the bit plane before thresholding

    Returns
    -------
    fp : lsst.afw.detection.detectionLib.FootprintSet
        Footprints assoicated with detected objects.
    """
    import lsst.afw.detection as afwDetect

    mask = masked_image.getMask() if mask is None else mask
    thresh_type = getattr(afwDetect.Threshold, thresh_type.upper())
    thresh = afwDetect.Threshold(thresh, thresh_type)
    fp = afwDetect.FootprintSet(masked_image, thresh, '', npix)
    if rgrow is not None:
        fp = afwDetect.FootprintSet(fp, rgrow, isogrow)
    if plane_name:
        mask.addMaskPlane(plane_name)
        if clear_mask:
            mask.clearMaskPlane(mask.getMaskPlane(plane_name))
        fp.setMask(mask, plane_name)
    return fp


def viz(image, transparency=75, frame=1, 
        colors=[('THRESH_HIGH', 'magenta'), ('THRESH_LOW', 'yellow')]):
    import lsst.afw.display as afwDisplay
    disp = afwDisplay.Display(frame)
    for name, color in colors:
        disp.setMaskPlaneColor(name, color) 
    disp.setMaskTransparency(transparency)
    disp.mtv(image)
    return disp
