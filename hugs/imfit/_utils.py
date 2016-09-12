from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

__all__ = ['read_results']

def read_results(fn, model='sersic'):
    """
    Read the output results file from imfit. 

    Parameters
    ----------
    fn : string
        Imfit file name.
    model : string, optional
        The model used in imfit's fit.

    Returns
    -------
    The model parameters in the same order as 
    they are given in the output file and the 
    reduced chi-square value. 
    """
    
    file = open(fn, 'r')
    lines = file.readlines()
    file.close()

    comments = [l for l in lines if l[0]=='#']
    params = [l for l in lines if l[0]!='#' if l[:2]!='\n' if l[0]!='F']

    reduced_chisq = float([c for c in comments if 
                           c.split()[1]=='Reduced'][0].split()[-1])

    if model=='sersic':
        x0 = float(params[0].split()[1])
        y0 = float(params[1].split()[1])
        pa = float(params[2].split()[1])
        ell = float(params[3].split()[1])
        n = float(params[4].split()[1])
        I_e = float(params[5].split()[1])
        r_e = float(params[6].split()[1])
        return x0, y0, pa, ell, n, I_e, r_e, reduced_chisq
