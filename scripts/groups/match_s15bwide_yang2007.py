#!/usr/bin/env python 

"""
Cross-match Yang 2007 galaxy group catalog (based on SDSS)
with the HSC catalog with the input region.
"""

import sys
import numpy as np
from astropy.table import Table, vstack
from toolbox.cats import crossmatch 
catDIR = '../data/catalogs/'

assert len(sys.argv)==5, '\n **** usage: '+sys.argv[0]+' ra_min ra_max dec_min dec_max'

ralims = [sys.argv[1], sys.argv[2]]
declims = [sys.argv[3], sys.argv[4]]
Ngal_min = 4 # min number of galaxies in group
maxsep = 1.5 # arcsec

print 'getting hsc HSCwide12H cat'
poslabel = '_ra_'+ralims[0]+'_'+ralims[1]+'_dec_'+declims[0]+'_'+declims[1]
hscfile = 'HSC/hsc_s15bwide'+poslabel+'.csv'
# file formating not consistent
if (ralims==['325','350']) or (ralims==['14','25']):
    hsc = Table.read(catDIR+hscfile) 
else:
    hsc = Table.read(catDIR+hscfile, format='csv', guess=False, comment='#')
print len(hsc), 'total objects in HSC catalog'

print 'getting yang catalog, Ngal_min =', Ngal_min
print 'maxsep =', maxsep, 'arcsec'
yang = Table.read(catDIR+'Yang/yang_modelC_all.txt', format='ascii')
yang = yang[yang['Ngal']>=Ngal_min]
print len(yang), 'galaxies in yang'

# we only want child objects
hsc = hsc[hsc['parent']!=0]
#hsc = hsc[hsc['i_deblend_nchild']==0]
print len(hsc), 'child objects in HSC catalog'

# change the default hsc catalog column names 
try: 
    hsc.rename_column('# id', 'id')
except KeyError:
    pass
try:
    hsc.rename_column('ra2000', 'ra')
    hsc.rename_column('decl2000', 'dec')
except KeyError:
    pass

print 'matching catalogs all galaxies'
yang_match, hsc_match, seps = crossmatch(yang, hsc, maxsep, return_seps=True)

# add galaxy properties to output catalog
hsc_match['group_id'] = yang_match['group_id']
hsc_match['bright'] = yang_match['bright']
hsc_match['match_sep'] = seps
hsc_match['z'] = yang_match['z']
hsc_match['Ngal'] = yang_match['Ngal']
hsc_match['Mh_Lest'] = yang_match['Mh_Lest']
hsc_match['Mh_Mest'] = yang_match['Mh_Mest']
hsc_match['g-r'] = yang_match['g-r']
hsc_match['Mr'] = yang_match['Mr']

# only keep groups with the bcg in hsc
hsc_match = hsc_match.group_by('group_id').groups.filter(lambda _t, _k : 1 in _t['bright'])
print len(hsc_match), 'galaxies matched'

fn_all =  '../data/mycats/hsc_yang_N'+str(Ngal_min)+poslabel+'.fits'
print 'writing catalog to', fn_all
hsc_match.write(fn_all, overwrite=True)
