from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
hscdir = os.path.join(os.environ.get('DATA_DIR'), 'hsc')

__all__ = ['load_pointings']

def load_pointings(band='i'):
    """
    Return the current HSC wide pointings in
    the given band.
    """
    from astropy.table import Table
    fn = 'ObservedWidePointings.lst'  
    fn = os.path.join(hscdir, fn)
    ra = []
    dec = []
    with open(fn) as file:
        for line in iter(file):
            data = line.split('|')
            if data[1][-1]==band:
                ra.append(float(data[2]))
                dec.append(float(data[3]))
    coords = Table([ra, dec], names=['ra', 'dec'])
    return coords
