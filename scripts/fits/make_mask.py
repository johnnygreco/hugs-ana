#!/tigress/HSC/LSST/stack_20160915/Linux64/miniconda2/3.19.0.lsst4/bin/python

import os
import numpy as np
from astropy.table import Table
from argparse import ArgumentParser
import lsst.afw.image 
import hugs

path = os.path.join(os.environ.get('HUGS_PIPE_IO'), 
                    'candy-cutouts/20170130-143629')
temp = os.path.join(os.environ.get('HUGS_PIPE_IO'), 'temp-io') 

parser = ArgumentParser()
parser.add_argument('candy_num', type=int)
parser.add_argument('--gal_pos', type=str, default='center')
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

if args.gal_pos=='center':
    gal_pos = args.gal_pos
else:
    pos = args.gal_pos.split(',')
    gal_pos = float(args.gal_pos[0]), float(args.gal_pos[1])
mask_kwargs['gal_pos'] = gal_pos

num = args.candy_num
indir= args.path

files = [f for f in os.listdir(indir) if 
         f.split('-')[-1]=='wide.fits' and int(f.split('-')[1])==num]

for fn in files:
    mi = lsst.afw.image.MaskedImageF(os.path.join(indir, fn))
    mask_fn = os.path.join(args.outdir, 'mask-'+fn)
    hugs.imfit.make_mask(mi, out_fn=mask_fn, **mask_kwargs)
