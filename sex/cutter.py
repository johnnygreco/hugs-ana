
from __future__ import print_function

__all__ = ['cuts', 'apply_cuts']

import numpy as np

cuts = {'min' : {'FLUX_RADIUS' : 9, 'FWHM_IMAGE' : 20.0},
        'max' : {'FLAGS' : 4},
       }
        
def apply_cuts(cat):
    """
    Apply selection cuts to input catalog. 
    """

    min_mask = np.ones(len(cat), dtype=bool)
    for key, min_val in cuts['min'].iteritems():
        print (key, min_val)
        min_mask[cat[key] < min_val] = False

    max_mask = np.ones(len(cat), dtype=bool)
    for key, max_val in cuts['max'].iteritems():
        print (key, max_val)
        max_mask[cat[key] > max_val] = False

    mask = min_mask & max_mask

    return cat[mask]
