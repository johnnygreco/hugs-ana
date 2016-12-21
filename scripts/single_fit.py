#!/Users/protostar/anaconda/envs/lsst/bin/python

import os
import numpy as np
from astropy.table import Table
from argparse import ArgumentParser
import hugs

path = os.path.join(os.environ.get('LOCAL_DATA'), 'hsc/stamps/candy/')
temp = os.path.join(os.environ.get('LOCAL_DATA'), 'TEMP') 

parser = ArgumentParser()
parser.add_argument('group_id', type=str)
parser.add_argument('candy_num', type=int)
parser.add_argument('-p', '--path', type=str, default=path)
parser.add_argument('-o', '--outdir', type=str, default=temp)

for k, v in hugs.tasks.DEFAULT_MASK.items():
    if k!='sep_extract_kws':
        parser.add_argument('--'+k, type=float, default=v)
    else:
        for k2, v2 in v.items():
            parser.add_argument('--'+k2, type=float, default=v2)

args = parser.parse_args()

mask_kwargs = {}
for k, v in hugs.tasks.DEFAULT_MASK.items():
    if k!='sep_extract_kws':
        mask_kwargs[k] = getattr(args, k)
    else:
        sep_extract_kws = {}
        for k2, v2 in v.items():
            sep_extract_kws[k2] = getattr(args, k2)
        mask_kwargs[k] = sep_extract_kws

group_dir = 'group-'+args.group_id
rundir = os.path.join(args.path, group_dir)

num = args.candy_num
cat = Table.read(os.path.join(rundir, 'candy.csv'))
pa = cat['orientation'][num] * 180.0/np.pi
pa = 90 + pa
ell = cat['ellipticity'][num]
init_params = {'PA': [pa, 0, 180],
	       'ell': [ell, 0, 0.999]}
hugs.tasks.fit_candy(num, rundir, args.outdir, init_params,
                     mask_kwargs=mask_kwargs)
