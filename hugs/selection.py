"""
Functions for the selection of candidates from the hugs-pipe catalog.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
from astropy.table import Table
from . import utils

__all__ = ['cutter', 'MIN_CUTS', 'MAX_CUTS']

##################################
# Default selection cuts
##################################

MIN_CUTS = {'a_3_sig': 2.5,
            'r_circ': 1.95,
            'mu_3':24.0}
MAX_CUTS = {'mag_ell': 23.0}


def cutter(cat, min_cuts=MIN_CUTS, max_cuts=MAX_CUTS, 
           verbose=True, return_mask=False):
    """
    Make selection cuts on input catalog.

    Parameters
    ----------
    cat : astropy.table.Table
        Input catalog.
    min_cuts : dict, optional
        Minimum params and values to cut.
    max_cuts : dict, optional
        Maximum params and values to cut.
    verbose : bool, optional
        If True, print lots of info.
    return_mask : bool, optional
        If True, also return the cutting mask.

    Returns 
    -------
    cat[mask] : ndarray
        Cut catalog
    mask : ndarray, if return_mask=True 
        Mask that will cut all objects that don't 
        pass the selection cuts.
    """

    if verbose: 
        print(len(cat), 'objects in cat before cuts')

    min_mask = np.ones(len(cat), dtype=bool)
    for key, min_val in min_cuts.items():
        if min_val is not None:
            if verbose: 
                print('cutting', key, 'at', min_val)
            min_mask[cat[key] <= min_val] = False

    max_mask = np.ones(len(cat), dtype=bool)
    for key, max_val in max_cuts.items():
        if max_val is not None:
            if verbose: 
                print('cutting', key, 'at', max_val)
            max_mask[cat[key] >= max_val] = False

    mask = min_mask & max_mask
    if verbose: 
        print(mask.sum(), 'objects will be cut')

    return (cat[mask], mask) if return_mask else cat[mask]
