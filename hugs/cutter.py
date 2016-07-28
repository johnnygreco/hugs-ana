
from __future__ import print_function

__all__ = ['cuts', 'apply_cuts']

import numpy as np

min_cuts = {
            'FLUX_RADIUS' : 9, 
            'FWHM_IMAGE'  : 20.0, 
           }

max_cuts = {'FLAGS' : 4}

cuts = {'min' : min_cuts, 'max' : max_cuts}
        
def apply_cuts(cat):
    """
    Apply selection cuts to input catalog. 
    """

    print(len(cat), 'objects in cat before cuts')

    min_mask = np.ones(len(cat), dtype=bool)
    for key, min_val in cuts['min'].iteritems():
        print('cutting', key, 'at', min_val)
        min_mask[cat[key] < min_val] = False

    max_mask = np.ones(len(cat), dtype=bool)
    for key, max_val in cuts['max'].iteritems():
        print('cutting', key, 'at', max_val)
        max_mask[cat[key] > max_val] = False

    mask = min_mask & max_mask
    cat = cat[mask]

    print(len(cat), 'objects in cat after cuts')

    return cat
