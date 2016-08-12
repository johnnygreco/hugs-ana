#!/usr/bin/env python 

# Combine the group (HSC) catalogs from different regions into
# one master catalog. 

import os
from astropy.table import Table, vstack

mycatDIR = '../data/mycats/'

colnames = ['id', 'parent', 'tract', 'patch', 'ra', 'dec', 'group_id', 'bright',
            'match_sep', 'z', 'Ngal', 'Mh_Lest', 'Mh_Mest', 'g-r', 'Mr']

files = [f for f in os.listdir(mycatDIR) if ((f[0]!='.') and f.split('_')[2]!='all')]
print(files[0])
hsc_yang = Table.read(mycatDIR+files[0])[colnames]

for f in files[1:]:
    print(f)
    hsc_yang = vstack([hsc_yang, Table.read(mycatDIR+f)[colnames]])
hsc_yang.write(mycatDIR+'hsc_yang_all_regions.fits', overwrite=True)
