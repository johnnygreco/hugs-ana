
__all__ = ['ring']

import numpy as np

def ring(r_inner, r_outer, dtype=np.int):
    """
    Generate a 2D ring footprint.

    Paramters
    ---------
    r_inner : int
        The inner radius of ring in pixels.
    r_outer : int
        The outer radius of ring in pixels.
    dtype : data type, optional
        The data type of the output array

    Returns
    -------
    fp : 2D ndarray
        The ring footprint with 1's in the 
        annulus and 0's everywhere else.
    """
    assert r_outer >= r_inner, 'must have r_outer >= r_inner'
    x = np.arange(-int(r_outer), int(r_outer)+1)
    r = np.sqrt(x**2 + x[:,None]**2) 
    annulus = (r>=r_inner) & (r<=r_outer)
    r[annulus] = 1
    r[~annulus] = 0
    fp = r.astype(dtype)
    return fp
