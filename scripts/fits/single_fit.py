#!/tigress/HSC/LSST/stack_20160915/Linux64/miniconda2/3.19.0.lsst4/bin/python

import os
import numpy as np
from astropy.table import Table
from argparse import ArgumentParser
import hugs

path = os.path.join(os.environ.get('HUGS_PIPE_IO'), 
                    'candy-cutouts/20170130-143629')
temp = os.path.join(os.environ.get('HUGS_PIPE_IO'), 'temp-io') 

parser = ArgumentParser()
parser.add_argument('candy_num', type=int)
parser.add_argument('-p', '--path', type=str, default=path)
parser.add_argument('-o', '--outdir', type=str, default=temp)
parser.add_argument('--no_psf', action='store_true')

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

num = args.candy_num
rundir = args.path
cat = Table.read(os.path.join(rundir, 'candy.csv'))

pa = cat['PA'][num]    
ell = cat['ell'][num]
n = cat['n'][num]
I_e = cat['I_e(i)'][num]
r_e = cat['r_e(i)'][num]*(1/0.168)
init_params = {
    'PA': [pa, 0, 180],
    'ell': [ell, 0, 0.999],
    'n': [n, 0.001, 5],
    'I_e': I_e,
    'r_e': r_e
}

results = hugs.tasks.fit_candy(
    num, rundir, args.outdir, init_params,
    mask_kwargs=mask_kwargs, use_psf=not args.no_psf)

out_fn = 'candy-{}-imfit-params.csv'.format(args.candy_num)
results.write(os.path.join(args.outdir, out_fn))
