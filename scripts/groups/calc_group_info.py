#!/usr/bin/env python 

import numpy as np
from astropy.table import Table, vstack
from toolbox.cosmo import Cosmology
h=0.7; omegaM0=0.3; omegaL0=0.7
cosmo = Cosmology(h, omegaM0, omegaL0)

# get combined hsc+yang catalog for all regions
mycatDIR = '../data/mycats/'
hsc_yang = Table.read(mycatDIR+'hsc_yang_all_regions.fits')

# keep only the bcgs
# need to sort for yang indexing
hsc_yang.sort('group_id') 
hsc_yang = hsc_yang[hsc_yang['bright']==1]

# get group info
group = np.loadtxt('../data/catalogs/Yang/group_DR7/modelC_group', skiprows=3, usecols=(0,1,2,3,6,7))
group = Table([group[:,i] for i in range(group.shape[1])], names=('group_id', 'ra', 'dec', 'z', 'Mh_Lest', 'Mh_Mest'),\
                                                                dtype=(int, 'f8', 'f8', 'f8', 'f8', 'f8'))
# only want groups in hsc
# note that the group ids start with group 1 (not zero)
group = group[hsc_yang['group_id']-1]

group['Ngal'] = hsc_yang['Ngal']

D_A = np.array([cosmo.D_A(z) for z in group['z']])
D_L = np.array([cosmo.D_L(z) for z in group['z']])
group['D_A'] = D_A
group['D_L'] = D_L

group['tract'] = hsc_yang['tract']
group['patch'] = hsc_yang['patch']

print group

group.write('../data/groups/group_info.csv')
