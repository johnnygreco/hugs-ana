#!/tigress/HSC/LSST/stack_20160915/Linux64/miniconda2/3.19.0.lsst4/bin/python

import os
import hugs
import numpy as np
import pandas as pd
import schwimmbad
import mpi4py.MPI as MPI
from astropy.table import Table

def worker(source):
    """
    Do some work.
    """
    num = source['num']
    rundir = source['rundir']
    save_figs = source['save_figs']
    use_psf = not source['no_psf']
    imfitdir = os.path.join(rundir, 'imfit')

    # get initial guess parameters
    pa = cat['PA'][num]
    ell = cat['ell'][num]
    n = cat['n'][num]
    I_e = cat['I_e(i)'][num]
    r_e = cat['r_e(i)'][num]*(1/0.168)
    init_params = {'PA': [pa, 0, 180],
                   'ell': [ell, 0, 0.999],
                   'n': [n, 0.001, 5.0],
                   'I_e': I_e,
                   'r_e': r_e}
    results = hugs.tasks.fit_candy(
        num, rundir, imfitdir, init_params, save_figs, tract=source['tract'],
        patch=source['patch'], use_psf=use_psf)
    out_fn = os.path.join(imfitdir, 'candy-{}-imfit-params.csv'.format(num))
    results.write(out_fn)


if __name__=='__main__':
    from argparse import ArgumentParser
    rank = MPI.COMM_WORLD.Get_rank()
    path = os.path.join(os.environ.get('HUGS_PIPE_IO'),
                        'candy-cutouts/20170130-143629')

    parser = ArgumentParser()
    parser.add_argument('-p', '--path', type=str, default=path)
    parser.add_argument('--no_psf', action='store_true')
    parser.add_argument('--save_figs', action='store_false')
    parser.add_argument('--bands', type=str, default='GRI')
    parser.add_argument('--cat_fn', type=str, default='candy.csv')

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ncores", dest="n_cores", default=1, type=int)
    group.add_argument("--mpi", dest="mpi", default=False, action="store_true")

    args = parser.parse_args()

    cat_fn = os.path.join(args.path, args.cat_fn)
    cat = Table.read(cat_fn)

    # get number of candidates
    stamp_files = [f for f in os.listdir(args.path) if
                   f.split('-')[-1]=='wide.fits']
    assert len(stamp_files)%len(args.bands)==0
    num_candy = len(stamp_files)//len(args.bands)
    assert len(cat)==num_candy

    cat['num'] = np.arange(num_candy)
    cat['rundir'] = args.path
    cat['save_figs'] = args.save_figs
    cat['no_psf'] = args.no_psf

    # all imfit results will be saved in imfit directory
    if rank==0:
        imfitdir = os.path.join(args.path, 'imfit')
        hugs.utils.mkdir_if_needed(imfitdir)

    pool = schwimmbad.choose_pool(mpi=args.mpi, processes=args.n_cores)
    list(pool.map(worker, cat))
    pool.close()

    if rank==0:
        df = []
        for num in np.arange(num_candy):
            fn = 'candy-{}-imfit-params.csv'.format(num)
            fn = os.path.join(imfitdir, fn)
            df.append(pd.read_csv(fn))
            os.remove(fn)
        df = pd.concat(df, ignore_index=True)
        out_fn = os.path.join(imfitdir, 'candy-imfit-params.csv')
        df.to_csv(out_fn, index=False)
