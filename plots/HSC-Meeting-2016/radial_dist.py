#!/usr/bin/env python 

import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table, vstack
import matplotlib.lines as mlines
plt.style.use('jpg')
cmap = plt.cm.rainbow

import hugs
from toolbox.astro import angsep
from toolbox.cosmo import Cosmology
cosmo = Cosmology()
h = cosmo.h 

r180 = hugs.yang_r180
results_dir = '../../results/'
group_ids = [1925, 3765, 4736, 6112, 8453, 12885, 7572, 8524, 9436]
#group_ids.remove(1925)
#group_ids.remove(3765)
#group_ids.remove(7572)
#group_ids.remove(6112)

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

n, bins, patches = ax.hist(candy['sep_rh_Lest'], bins=9, lw=2.5, 
                           histtype='step', range=(0, candy['sep_rh_Lest'].max()))
h1_line = mlines.Line2D([], [], color=patches[0].get_ec(), label='UDG candidates', lw=2.5)
n, bins, patches = ax.hist(brights['sep_rh_Lest'], bins=bins, histtype='step', lw=2.5)
h2_line = mlines.Line2D([], [], color=patches[0].get_ec(), label='Bright group members', lw=2.5)
ax.set_xlabel(r'$r/r_{180}$')
ax.set_ylabel(r'Number')
ax.legend(loc='upper right', fontsize=20, handles=[h1_line, h2_line])
ax.minorticks_on()
ax.fill_between(np.linspace(0,4.5,10), 1, 3, color='gray', alpha=0.2)
ax.fill_between(np.linspace(0,4.5,10), 1, 3, facecolor='none', edgecolor='k', alpha=0.5, hatch='//')
ax.set_ylim(0,40)

fig.savefig('/Users/protostar/Desktop/radial_dist.pdf')
    
try: import RaiseWindow
except: pass

plt.show()
