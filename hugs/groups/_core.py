from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
from astropy.table import Table
yangdir = os.path.join(os.environ.get('DATA_DIR'), 'catalogs/Yang')

__all__ = ['get_group_table']

def get_group_table():
    """
    Return an astropy table of parameters for Yang groups.
    """
    fn = os.path.join(yangdir, 'group_DR7/modelC_group')
    groups = np.loadtxt(fn, skiprows=3, usecols=(0,1,2,3,6,7))
    groups = Table([groups[:,i] for i in range(groups.shape[1])],
                   names=('group_id', 'ra', 'dec', 'z', 'Mh_Lest', 'Mh_Mest'),
                   dtype=(int, 'f8', 'f8', 'f8', 'f8', 'f8'))

    return groups
