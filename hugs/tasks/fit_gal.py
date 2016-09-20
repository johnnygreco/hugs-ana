"""
Use SEP and imfit to perform 2D galaxy fits. 
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

from .. import imtools
from .. import imfit
from .. import photo
from .. import models
 
__all__ = ['fit_gal']


DEFAULT_PARAMS = {'X0': None , # set by gal_pos
                  'Y0': None,  # set by gal_pos
                  'PA': [18., 0, 360], 
                  'ell': [0.2,0,1], 
                  'n': [0.5,0,5], 
                  'I_e': 1.0, 
                  'r_e': 5}

DEFAULT_MASK = {'thresh': 1.5,
                'backsize': 100, 
                'backffrac': 0.5, 
                'sig': False,
                'mask_from_hsc': True, 
                'seg_rmin': 100.0, 
                'obj_rmin': 20.0, 
                'grow_sig': 6.0, 
                'mask_thresh': 0.02, 
                'grow_obj': 3.0, 
                'sep_extract_params': {'deblend_nthresh': 16, 
                                       'deblend_cont': 0.001}}


def fit_gal(img_fn, mask_fn=2, var_fn=3, gal_pos='center', init_params={}, 
            prefix='fit', clean=True, img_hdu=1, **kwargs):
    """
    Perform 2D galaxy fit using the hugs.imfit and hugs.photo modules, 
    which use imfit and SEP. Most of the work in this function is 
    getting all the input parameters ready for imfit (which uses 
    file names) and SEP (which uses numpy arrays).

    Parameters
    ----------
    img_fn : string
        Fits file name of image (can be multi-extension).
    mask_fn : int, str, or None, optional
        If int, the index of the hdulist in img_fn. If str, 
        the fits file name of the mask. If None, no initial mask 
        will be used when making the photometry mask.
    var_fn : int, str, or None, optional
        If int, the index of the hdulist in img_fn. If str, 
        the fits file name of the variance. If None, the variance
        will not be used.
    gal_pos : array-like, optional
        The position of the galaxy of interest in pixels. If 'center', 
        then the center of the image will be assumed.
    init_params : dict, optional
        Initial imfit parameters that are different from defaults given 
        by DEFAULT_PARAMS.
    prefix : str, optional
        Prefix for all files generate by this function. Can include
        full path if you want files saved in a specific directory. 
    clean : bool, optional
        If True, delete the photometry mask and imfit config files
        that are created in this function. 
    img_hdu : int, optional
        Index of the image if a multi-extension file is given.
    **kwargs : dict 
        Any parameter for hugs.photo.make_mask except img, mask, 
        and out_fn, which are set in this function. 

    Returns
    -------
    sersic : hugs.models.Sersic 
        Object containing the best-fit sersic model and associated
        derived parameters.
        
    Notes
    -----
    - If you want to use the variance map when making the photometry
      mask, pass sig=True as a kwargs. By default, this is set to False.
    - If using a multi-extension fits file, then the image, mask and 
      variance must be in the same fits file. 
    """

    ######################################################################
    # Setup image file names for imfit, and get the ndarrays for SEP. 
    # If the image file is a multi-extension fits file, the file names 
    # become 'file.fits[hdu_index]'.  
    ######################################################################

    if (type(mask_fn)!=str) and (type(var_fn)!=str):
        header, img, mask, var = imtools.open_fits(img_fn)
        mask_fn = img_fn+'['+str(mask_fn)+']' if mask_fn else None
        var_fn = img_fn+'['+str(var_fn)+']' if var_fn else None
        img_fn = img_fn+'['+str(img_hdu)+']' 
    elif (type(mask_fn)!=int) and (type(var_fn)!=int):
        img = fits.getdata(img_fn)
        mask = fits.getdata(mask_fn) if mask_fn else None
        var = fits.getdata(var_fn) if var_fn else None
    else: 
        raise Exception('Invalid file format.')

    ######################################################################
    # Get the parameters for hugs.photo.make_mask from the kwargs.
    ######################################################################

    mask_params = DEFAULT_MASK.copy()
    for k,v in list(kwargs.items()):
        if k in list(DEFAULT_MASK.keys()):
            mask_params[k] = v
        else:
            raise Exception('Invalid input parameter: '+k)

    ######################################################################
    # If needed, set the ndarrays for hugs.photo.make_mask. If sig=True 
    # is given, then the sigma image will be used for mask making. 
    ######################################################################

    if mask_params['sig']:
        assert var_fn is not None, 'Must give var file when sig != None'
        mask_params['sig'] = np.sqrt(var)
    else:
        mask_params['sig'] = None
    if mask_params['mask_from_hsc']:
        assert mask_fn is not None, 'Must give var file with mask_from_hsc'
        mask_params['mask'] = mask
    else:
        mask_params['mask'] = None


    ######################################################################
    # Get the coords of the galaxy of interest and set the imfit config.
    ######################################################################

    if gal_pos=='center':
        gal_pos = img.shape[1]/2, img.shape[0]/2
    mask_params['gal_pos'] = gal_pos

    imfit_config = DEFAULT_PARAMS.copy()
    for k, v in list(init_params.items()):
        imfit_config[k] = v
    imfit_config['X0'] = [gal_pos[0], gal_pos[0]-30, gal_pos[0]+30]
    imfit_config['Y0'] = [gal_pos[1], gal_pos[1]-30, gal_pos[1]+30]

    ######################################################################
    # Make the photometry mask and save it to a fits file.
    ######################################################################

    photo_mask_fn = prefix+'_photo_mask.fits'
    photo_mask = photo.make_mask(img, out_fn=photo_mask_fn, 
                                 **mask_params)

    ######################################################################
    # Run imfit. The best-fit params will be saved to out_fn. 
    ######################################################################

    config_fn = prefix+'_config.txt'
    out_fn = prefix+'_bestfit_params.txt'
    results = imfit.run(img_fn, config_fn, photo_mask_fn, var_fn,
                        out_fn=out_fn, config=imfit_config)

    if clean:
        os.remove(config_fn)
        os.remove(photo_mask_fn)

    sersic = models.Sersic(results)

    return sersic
