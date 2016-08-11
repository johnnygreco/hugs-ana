"""
Collection of useful variables and functions for HSC-HUGs.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

__all__ = ['cuts', 'apply_cuts', 'bit_dict', 'get_bitmask_flags']

min_cuts = {'ISO0': 400, 'FLUX_RADIUS': 9}
max_cuts = {'FLAGS' : 3}
cuts = {'min' : min_cuts, 'max' : max_cuts}

def apply_cuts(cat):
    """
    Apply selection cuts to input catalog. 

    Parameters
    ----------
    cat : astropy.table.Table
        Catalog of objects detected by SExtractor. 

    Returns
    cat : astropy.table.Table
        The catalog with the selection cuts applied.
    """

    print(len(cat), 'objects in cat before cuts')

    min_mask = np.ones(len(cat), dtype=bool)
    for key, min_val in cuts['min'].items():
        print('cutting', key, 'at', min_val)
        min_mask[cat[key] <= min_val] = False
    max_mask = np.ones(len(cat), dtype=bool)
    for key, max_val in cuts['max'].items():
        print('cutting', key, 'at', max_val)
        max_mask[cat[key] >= max_val] = False
    mask = min_mask & max_mask
    cat = cat[mask]
    print(len(cat), 'objects in cat after cuts')
    return cat


bit_dict =  {1: 'BAD',                # Pixel is physically bad (a known camera defect)
             2: 'SATURATED',          # Pixel flux exceeded full-well
             4: 'INTERPOLATED',       # Pixel contains a value based on interpolation from neighbours.
             8: 'CR',                 # Cosmic Ray hit
             16: 'EDGE',              # Near the CCD edge
             32: 'DETECTED',          # Pixel is part of a source footprint (a detected source)
             64: 'DETECTED_NEGATIVE', # Pixel is part of a negative source footprint (in difference image)
             128: 'SUSPECT',          # Pixel is nearly saturated. It may not be well corrected for non-linearity.
             256: 'NO_DATA',          # (Coadd only) Pixel has no input data (between CCDs, beyond edge of frame)
             512: 'BRIGHT_OBJECT',    # 
             1024: 'CLIPPED',         # (Coadd only) Co-addition process clipped 1 or 2 (but not more) input pixels
             2048: 'CROSSTALK',       # Pixel location affected by crosstalk (and corrected)
             4096: 'NOT_DEBLENDED',   # 
             8192: 'UNMASKEDNAN'}     # A NaN occurred in this pixel in ISR (instrument signature removal - bias,flat,etc)

def get_bitmask_flags(decimal_sum):
    """
    Return the flags associated with the decimal sum 
    from the HSC bitmask

    Parameters
    ----------
    decimal_sum : int
        Decimal sum of powers of 2. 
    
    Returns
    -------
    flags : list of strings 
        All flag names implied by the input sum. 
    """
    decimal_mask_vals = 2**np.arange(len(bit_dict))
    on_bits = decimal_mask_vals[(decimal_sum & decimal_mask_vals)!=0]
    flags = [bit_dict[b] for b in on_bits]
    return flags 
