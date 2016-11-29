"""
Functions for the selection of candidates from the hugs-pipe catalog.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
import pandas as pd
from astropy.table import Table
from . import utils

__all__ = ['MIN_CUTS', 'MAX_CUTS', 'cutter', 'doubles_mask']

##################################
# Default selection cuts
##################################

MIN_CUTS = {'a_3_sig': 2.0,
            'r_circ_ell': 1.5,
            'mu_3_i': 23.0}
MAX_CUTS = {'num_edge_pix': 1}


def _max_r_vir_cut(cat, group_id, max_r_vir):
    """
    If we have the group_id, we can cut objects 
    that are greater than max_r_vir from the group. 
    """
    from .datasets import yang
    from toolbox.astro import angsep
    from toolbox.cosmo import Cosmology
    cosmo = Cosmology()
    props = ['ra', 'dec', 'z', 'Mh_Lest']
    ra, dec, z, logMh = yang.get_group_prop(group_id, props)
    D_A = cosmo.D_A(z)
    r180 = yang.r180(logMh, z)
    theta_180 = (r180/D_A)*180.0/np.pi
    seps = angsep(ra, dec, cat['ra'], cat['dec'], sepunits='degree')
    mask = seps < max_r_vir*theta_180
    return mask


def cutter(cat, min_cuts=MIN_CUTS, max_cuts=MAX_CUTS, verbose=True, 
           return_mask=False, group_id=None, max_r_vir=2.0):
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
    group_id : int, optional
        Galaxy group id. If given, will impose max 
        virial radius cut.
    max_r_vir : float, optional
        Max number of virial radii to be considered a candidate.

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

    if group_id is not None:
        if verbose:
            print('cutting objects outside {} r_vir'.format(max_r_vir))
        mask &= _max_r_vir_cut(cat, group_id, max_r_vir)

    if verbose: 
        print(mask.sum(), 'objects in cat after cuts')

    return (cat[mask], mask) if return_mask else cat[mask]


def doubles_mask(cat, min_sep=0.7, ra_col='ra', dec_col='dec'):
    """
    Build mask for double entries in a catalog. 
    Consider object within min_sep arcsec the same object

    Parameters
    ----------
    cat : astropy.table.Table or pandas DataFrame
        Input catalog.
    min_sep : float, optional
        Minimum separation (arcsec) to be consisdered separate objects.
    ra_col : string, optional
        RA column name.
    dec_col : string, optional
        Declination column name.

    Returns
    -------
    mask : ndarray
        Mask that when applied to cat will remove double entries. 

    Notes
    -----
    RA and dec must be in degrees. 
    """
    mask = np.ones(len(cat), dtype=bool)

    if type(cat)==Table:
        cat = cat.to_pandas()
    else:
        assert type(cat)==pd.core.frame.DataFrame

    for i, (_, series) in enumerate(cat.iterrows()):
        # don't search objects flagged as double entries
        x, y = series[[ra_col, dec_col]]
        if mask[i]==True:
            # very small angles, so euclid is okay
            dist_sq = np.sqrt((x - cat[ra_col].values)**2 + (y - cat[dec_col].values)**2)
            dist_sq *= 3600.0
            unique = dist_sq > min_sep
            unique[i] = True # it will certainly match itself
            mask &= unique   # double entries set to False
    return mask
