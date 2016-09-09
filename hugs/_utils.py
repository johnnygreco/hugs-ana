"""
Collection of useful variables and functions for HSC-HUGs.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

__all__ = ['pixscale', 'apply_cuts', 'bit_dict', 'bit_flag_dict', 
           'get_bitmask_flags', 'yang_r180', 'doubles_mask']

pixscale = 0.168 # arcsec/pixel

def apply_cuts(cat, z=0.05, min_reff=1.5, min_iso0=400, max_flags=3, sb_lo=23.99):
    """
    Apply selection cuts to input catalog. 

    Parameters
    ----------
    cat : astropy.table.Table
        Catalog of objects detected by SExtractor. 
    z : float, optional
        Galaxy group redshift
    min_reff : float, optional
        Cut at and below this effective radius in kpc.
    min_iso0 : int, optional
        Cut at and below this isophotal area (pixel^2).
    max_flags : int, optional
        Cut at and above this many flags 
    sb_lo : float, optional
        Cut when central SB is lower (i.e., brighter) than
        this value in mag/arcsec

    Returns
    cat : astropy.table.Table
        The catalog with the selection cuts applied.
    """
    import astropy.units as u
    from toolbox.cosmo import Cosmology
    
    cosmo = Cosmology()
    kpc_per_pix = u.arcsec.to('radian')*pixscale*cosmo.D_A(z)*1e3
    min_flux_radius = (min_reff/kpc_per_pix) # pixels

    min_cuts = {'ISO0': min_iso0, 
                'FLUX_RADIUS': min_flux_radius,
                'MU_APER_2': sb_lo}
    max_cuts = {'FLAGS' : max_flags}
    cuts = {'min' : min_cuts, 'max' : max_cuts}
    
    print(len(cat), 'objects in cat before cuts')

    min_mask = np.ones(len(cat), dtype=bool)
    for key, min_val in cuts['min'].items():
        if min_val is not None:
            print('cutting', key, 'at', min_val)
            min_mask[cat[key] <= min_val] = False
    max_mask = np.ones(len(cat), dtype=bool)
    for key, max_val in cuts['max'].items():
        if max_val is not None:
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

bit_flag_dict = dict((v,k) for k,v in bit_dict.items())


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


def yang_r180(Mh, z, h=0.693):
    """
    Virial radius of a group given its halo mass
    and redshift. From Yang et al. 2007.

    Parameters
    ----------
    Mh : float
        Halo mass in Solar masses.
    z : float
        Redshift to galaxy group.
    h : float, optional
        Little h. Uses WMAP9 value by default.

    Returns
    -------
    r180 : float
        The groups virial radius.
    """
    r180 = (1.26/h)*(Mh/(1.0e14/h))**(1.0/3.0)/(1+z) # Mpc
    return r180


def doubles_mask(cat, min_sep=0.7):
    """
    Build mask for double entries in a catalog. 
    Consider object within min_sep arcsec the same object
    """
    from toolbox.astro import angsep
    mask = np.ones(len(cat), dtype=bool)
    for i, (ra, dec) in enumerate(cat['ALPHA_J2000','DELTA_J2000']):
        # don't search objects flagged as double entries
        if mask[i]==True:
            seps = angsep(ra, dec, cat['ALPHA_J2000'], cat['DELTA_J2000'])
            unique = seps > min_sep
            unique[i] = True # it will certainly match itself
            mask &= unique   # double entries set to False
    return mask
