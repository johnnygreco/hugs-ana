#!/usr/bin/env python 

import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table, vstack
plt.style.use('jpg')

import hugs
from toolbox.astro import angsep
from toolbox.cosmo import Cosmology
cosmo = Cosmology()
h = cosmo.h 

r180 = lambda Mh, z: (1.26/h)*(Mh/(1.0e14/h))**(1.0/3.0)/(1+z) # Mpc
results_dir = '../../results/'
group_ids = [1925, 3765, 4736, 6112, 8453, 12885]

yang_groups = hugs.datasets.load_yang_groups()
yang_gals = hugs.datasets.load_yang_gals()

fig, ax = plt.subplots()

candy = Table()
brights = Table()

for _id in group_ids:
    fn = results_dir+'group_'+str(_id)+'/viz_cat.txt'
    tab = Table.read(fn, format='ascii')
    tab_brights = yang_gals[yang_gals['group_id']==_id]
    ginfo = yang_groups[_id-1]
    assert ginfo['group_id']==_id

    rh_Lest = r180(10**ginfo['Mh_Lest'], ginfo['z'])
    rh_Mest = r180(10**ginfo['Mh_Mest'], ginfo['z'])

    sep = angsep(ginfo['ra'], ginfo['dec'], tab['ALPHA_J2000'], tab['DELTA_J2000'], sepunits='radian')
    sep *= cosmo.D_A(ginfo['z'])
    sep_rh_Lest = sep/rh_Lest
    sep_rh_Mest = sep/rh_Mest
    tab['sep'] = sep
    tab['sep_rh_Lest'] = sep_rh_Lest
    tab['sep_rh_Mest'] = sep_rh_Mest

    sep_brights = angsep(ginfo['ra'], ginfo['dec'], tab_brights['ra'], tab_brights['dec'], sepunits='radian')
    sep_brights *= cosmo.D_A(ginfo['z'])
    sep_rh_Lest = sep_brights/rh_Lest
    sep_rh_Mest = sep_brights/rh_Mest
    tab_brights['sep'] = sep_brights
    tab_brights['sep_rh_Lest'] = sep_rh_Lest
    tab_brights['sep_rh_Mest'] = sep_rh_Mest

    candy = vstack([candy, tab])
    brights = vstack([brights, tab_brights])

n, bins, patched = ax.hist(candy['sep_rh_Lest'], bins=8, 
                           histtype='step', range=(0, candy['sep_rh_Lest'].max()))
ax.hist(brights['sep_rh_Lest'], bins=bins, histtype='step')
ax.set_xlabel(r'$r/r_{180}$')
ax.set_ylabel(r'Number of Candidates')
ax.minorticks_on()
    
try: import RaiseWindow
except: pass

plt.show()
