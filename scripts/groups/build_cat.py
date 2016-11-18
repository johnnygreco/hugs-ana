#!/Users/protostar/anaconda/envs/lsst/bin/python
"""
Cross-match group catalog and HSC pointings.
"""

from __future__ import division, print_function

import os
import numpy as np
import hugs
from spherical_geometry.polygon import SphericalPolygon

import lsstutils
import lsst.daf.persistence
from toolbox.cats import crossmatch
from toolbox.cosmo import Cosmology
cosmo = Cosmology()

pointings = hugs.datasets.hsc.load_pointings('i')
groups = hugs.datasets.yang.load_groups()

Mh_min = 12.5
Mh_max = 14.0
max_z = 0.02
max_sep = 0.75 # degrees
num_r_vir = 2.0

cut = (groups['Mh_Lest'] >= Mh_min) & (groups['Mh_Lest'] <= Mh_max)
cut &= groups['z'] <= max_z
groups = groups[cut]

print(len(groups), 'groups after cuts')
print(len(pointings), 'wide i-band pointings')

groups_match, point_match, seps = crossmatch(
    groups, pointings, max_sep, sep_units='degree', return_seps=True)
print(len(groups_match), 'groups in footprint')

coord_lists = []
for g in groups_match:
    D_A = cosmo.D_A(g['z'])
    r_180 = hugs.datasets.yang.r180(g['Mh_Lest'], g['z'])
    theta_180 = (r_180/D_A)*180.0/np.pi
    cone = SphericalPolygon.from_cone(
        g['ra'], g['dec'], num_r_vir*theta_180, steps=30)
    ra, dec = list(cone.to_radec())[0]
    ra = ra + 360*(ra<0)
    ra = np.append(ra, g['ra'])
    dec = np.append(dec, g['dec'])
    coord_lists.append([(r,d) for r,d in zip(ra, dec)])

result = {}
dir = os.environ.get('HSC_DIR')
butler = lsst.daf.persistence.Butler(dir)
skymap = butler.get('deepCoadd_skyMap', immediate=True)
exist_mask = np.zeros(len(groups_match), dtype=bool)

for i, cl in enumerate(coord_lists):
    r, _ = lsstutils.tracts_n_patches(cl, skymap)
    does_exist = True
    for tract, patch in r:
        if not does_exist:
            break
        for band in ['G', 'R', 'I']:
            dataId = {'tract': tract, 'patch': patch, 'filter': 'HSC-'+band}
            fn = butler.get(
                'deepCoadd_calexp_filename', dataId, immediate=True)
            if not os.path.isfile(fn[0]):
                does_exist = False
                break
    if does_exist:
        exist_mask[i] = True
        result.update({groups_match['group_id'][i]: r})
groups_match = groups_match[exist_mask]

dir = '../../results/'
prefix = 'cat_z{}_Mh{}-{}'.format(max_z, Mh_min, Mh_max)
fn = prefix+'_tracts_n_patches.npy'
np.save(dir+fn, result)

fn = prefix+'_group_info.txt'
groups_match.write(dir+fn, format='ascii')
