#!/Users/protostar/anaconda/envs/lsst/bin/python

import os
import hugs
from argparse import ArgumentParser
path = os.path.join(os.environ.get('LOCAL_DATA'), 'hsc/stamps/candy/')

parser = ArgumentParser()
parser.add_argument('group_id', type=str)
parser.add_argument('-p', '--path', type=str, default=path)
parser.add_argument('--no_psf', action='store_true')
args = parser.parse_args()

group_dir = 'group-'+args.group_id
rundir = os.path.join(args.path, group_dir)

hugs.tasks.run_batch_fit(rundir, use_psf=not args.no_psf)
