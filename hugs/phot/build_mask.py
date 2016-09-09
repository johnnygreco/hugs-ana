
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .mask_utils import *
from .._utils import bit_flag_dict

def build_mask(img, thresh, backsize, backffrac=0.5, sig=None, 
               mask=None, minarea=5, kern='default', ftype='matched', 
               db_nthr=32, db_cont=0.005, clean=True, clean_param=1.0, 
               gal_pos='center'):
    """
    Parameters
    ----------

    Returns
    -------
    """
    if mask is not None:
        hsc_bad_mask = mask.copy()
        detected = bit_flag_dict['DETECTED']
        hsc_bad_mask[hsc_bad_mask==detected] = 0
    else:
        hsc_bad_mask = np.zeros(img.shape, dtype=int)

    if gal_pos=='center':
        gal_x, gal_y = (img.shape[0]/2, img.shape[1]/2)
    else:
        gal_x, gal_y = gal_pos

    obj, seg, bkg, img = detect_sources(
        img, thresh, backsize, backffrac, sig, mask, minarea, kern, 
        ftype, db_nthr, db_cont, clean, clean_param, True)
