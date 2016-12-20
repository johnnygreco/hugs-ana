""" Use SEP and imfit to perform 2D galaxy fits.  """
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


DEFAULT_PARAMS = {'X0': None , # If None, use center +/- 30 pix
                  'Y0': None,  # If None, use center +/- 30 pix
                  'PA': [18., 0, 360], 
                  'ell': [0.2, 0, 0.99], 
                  'n': [1.0, 0.01, 5], 
                  'I_e': 0.05, 
                  'r_e': 20.0}

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


def fit_gal(img_fn, mask_fn=2, var_fn=3, init_params={}, prefix='fit', 
            clean='both', img_hdu=1, visualize=False, photo_mask_fn=None,
            make_mask_kwargs={}, delta_pos=50.0, **kwargs):
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
    init_params : dict, optional
        Initial imfit parameters that are different from defaults given 
        by DEFAULT_PARAMS.
    prefix : str, optional
        Prefix for all files generate by this function. Can include
        full path if you want files saved in a specific directory. 
    clean : string, optional
        Files to remove after fitting (mask, config, or both).
    img_hdu : int, optional
        Index of the image if a multi-extension file is given.
    visualize : bool, optional
        If True, plot results.
    photo_mask_fn : string
        File name of photometry mask. If None, it will be created
        using sep. 
    make_mask_kwargs : dict, optional
        Any parameter for hugs.photo.make_mask except img, mask, 
        and out_fn, which are set in this function. Can also
    delta_pos : float, optional
        Uncertainty in position in pixels. Only used if X0=Y0=None, 
        in which case the center of the image is assumed. 

    Returns
    -------
    sersic : hugs.models.Sersic 
        Object containing the best-fit sersic model and associated
        derived parameters.
        
    Notes
    -----
    - If using a multi-extension fits file, then the image, mask and 
      variance must be in the same fits file. 
    """

    ######################################################################
    # Setup image file names for imfit, and get the ndarrays for SEP. 
    # If the image file is a multi-extension fits file, the file names 
    # become 'file.fits[hdu_index]'.  
    ######################################################################

    img_fn_init = img_fn
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
    # Get the parameters for hugs.photo.make_mask 
    ######################################################################

    mask_params = DEFAULT_MASK.copy()
    for k,v in list(make_mask_kwargs.items()):
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

    imfit_config = DEFAULT_PARAMS.copy()
    for k, v in list(init_params.items()):
        imfit_config[k] = v

    if imfit_config['X0'] is None:
        assert imfit_config['Y0'] is None
        gal_pos = img.shape[1]/2, img.shape[0]/2
        mask_params['gal_pos'] = gal_pos
        imfit_config['X0'] = [gal_pos[0], gal_pos[0]-delta_pos,
                              gal_pos[0]+delta_pos]
        imfit_config['Y0'] = [gal_pos[1], gal_pos[1]-delta_pos,
                              gal_pos[1]+delta_pos]
    else:
        if type(imfit_config['X0'])==list:
            gal_pos = imfit_config['X0'][0], imfit_config['Y0'][0]
        else:
            gal_pos = imfit_config['X0'], imfit_config['Y0']
        mask_params['gal_pos'] = gal_pos

    ######################################################################
    # Make the photometry mask and save it to a fits file.
    ######################################################################

    if photo_mask_fn is None:
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

    if visualize:
        imfit.viz.img_mod_res(img_fn_init, results, photo_mask_fn, 
                              figsize=(16,6), **kwargs)

    if (clean=='mask') or (clean=='both'):
        os.remove(photo_mask_fn)
    if (clean=='config') or (clean=='both'):
        os.remove(config_fn)

    sersic = models.Sersic(results)

    return sersic
