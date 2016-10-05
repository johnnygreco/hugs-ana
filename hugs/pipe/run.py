from __future__ import division, print_function

import os
import numpy as np
from . import utils
from ..utils import pixscale
HSC_DIR = os.environ.get('HSC_DIR')
THRESHOLDS = {'high': 18.0, 'low':3.0, 'med':4.0}
NPIX = {'high': 1, 'low':50, 'med':100}

def run(dataID, thresholds={}, npix={}, butler=None, assoc_radius=15.0, 
        kern_fwhm=3.5, data_dir=HSC_DIR, visualize=True):

    import lsstutils

    if type(dataID)==str:
        import lsst.afw.image
        exposure = lsst.afw.image.ExposureF(dataID)
    else:
        if butler is None:
            import lsst.daf.persistence
            butler = lsst.daf.persistence.Butler(data_dir)
        exposure = butler.get('deepCoadd_calexp', dataID, immediate=True)
    for k,v in list(thresholds.items()):
        THRESHOLDS[k] = v
    for k,v in list(npix.items()):
        NPIX[k] = v
    
    mi = exposure.getMaskedImage()
    mask = mi.getMask()
    mask.clearMaskPlane(mask.getMaskPlane('DETECTED'))
    mask.removeAndClearMaskPlane('DETECTED_NEGATIVE', True) 

    # smooth image at psf scale
    psf_sigma = utils.get_psf_sigma(exposure)
    mi_smooth = lsstutils.imgproc.smooth_gauss(mi, psf_sigma)
    rgrow = int(2.4*psf_sigma + 0.5)

    # image thesholding at low threshold
    fp_low = utils.image_threshold(
        mi_smooth, THRESHOLDS['low'], mask=mask,
        plane_name='THRESH_LOW', rgrow=rgrow, npix=NPIX['low'])

    # image thesholding at high threshold
    fp_high = utils.image_threshold(
        mi_smooth, THRESHOLDS['high'], mask=mask,
        plane_name='THRESH_HIGH', rgrow=rgrow, npix=NPIX['high'])

    # generate noise array 
    shape = mask.getArray().shape
    back_rms = mi.getImage().getArray()[mask.getArray()==0].std()
    noise_array = back_rms*np.random.randn(shape[0], shape[1])

    # get "association" segmentation image, which is non-zero for 
    # low-thresh footprints that are associated with high-thresh
    # footprints. Then, replace these sources with noise.
    assoc = utils.associate(mask, fp_low, radius=assoc_radius)
    exp_clone = exposure.clone()
    mi_clone = exp_clone.getMaskedImage()
    mi_clone.getImage().getArray()[assoc!=0] = noise_array[assoc!=0]
    if visualize:
        displays = []
        displays.append(utils.viz(exp_clone, 75, 1))

    # smooth with large kernel for detection
    fwhm = kern_fwhm/0.168 # pixels
    sigma = fwhm/(2*np.sqrt(2*np.log(2)))
    mi_clone_smooth = lsstutils.imgproc.smooth_gauss(mi_clone, sigma)

    # image thresholding at medium threshold for detection
    fp_med = utils.image_threshold(
        mi_clone_smooth, THRESHOLDS['med'], mask=mask,
        plane_name='DETECTED', npix=NPIX['med'])

    if visualize:
       displays.append(utils.viz(exposure, 60, 2))

    return displays if visualize else None
