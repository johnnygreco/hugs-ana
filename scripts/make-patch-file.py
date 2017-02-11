#!/Users/protostar/anaconda/envs/lsst/bin/python
from __future__ import division, print_function

import os
import numpy as np
import pandas as pd
import hugs
import lsstutils
import lsst.daf.persistence
from spherical_geometry.polygon import SphericalPolygon

use_full_pointings = True
if use_full_pointings:
    pointings = hugs.datasets.hsc.load_pointings(full=True)
else:
    pointings = hugs.datasets.hsc.load_pointings('i')
print(len(pointings), 'wide i-band pointings')

bands = 'GRI'
theta = 0.8 # degree

coord_lists = []
for p in pointings:
    cone = SphericalPolygon.from_cone(p['ra'], p['dec'], theta, steps=30)
    ra, dec = list(cone.to_radec())[0]
    ra = ra + 360*(ra<0)
    ra = np.append(ra, p['ra'])
    dec = np.append(dec, p['dec'])
    coord_lists.append([(r,d) for r,d in zip(ra, dec)])

butler = lsst.daf.persistence.Butler(os.environ.get('HSC_DIR'))
skymap = butler.get('deepCoadd_skyMap', immediate=True)

df = []
for i, cl in enumerate(coord_lists):
    print('***** coord list', i, '*****')
    r, _ = lsstutils.tracts_n_patches(cl, skymap)
    for tract, patch in r:
        does_exist = True
        for band in bands:
            dataId = {'tract': tract, 'patch': patch, 'filter': 'HSC-'+band}
            if not butler.datasetExists("deepCoadd_calexp", dataId):
                does_exist = False
                break
        if does_exist:
            print('tract:', tract, 'patch:', patch)
            df.append(pd.DataFrame({'tract': [tract], 'patch': [patch]}))
df = pd.concat(df, ignore_index=True)
df.drop_duplicates(inplace=True)
label = 'full' if use_full_pointings else 'all'
out_fn ='hsc-wide-patches-'+label+'.csv'
out_fn = os.path.join(os.environ.get('HUGS_PIPE_IO'), 'patch-files/'+out_fn)
df.to_csv(out_fn, index=False)
