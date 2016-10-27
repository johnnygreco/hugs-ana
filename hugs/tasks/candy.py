from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from astropy.table import Table

from .. import utils
from ..datasets import hsc

OUTDIR = os.path.join(utils.hugs_pipe_io, 'stamps')


def get_candy_stamps(cat, label=None, bands='GRI', outdir=OUTDIR):
    """
    Get postage stamps from database. 

    Parameters
    ----------
    cat : astropy.table.Table
        Source catalog (output from hugs_pipe).
    label : string, optional
        Label for stamps. If None, will use time.
    bands : string or list, optional
        Photometric bands to get. 
    outdir : string, optional
        Output directory.
    """
    
    if label is None:
        import time
        label = time.strftime("%Y%m%d-%H%M%S")

    stampdir = os.path.join(outdir, 'candies_'+label)
    utils.mkdir_if_needed(stampdir)

    new_cat_fn = os.path.join(stampdir, 'candy.cat')
    cat.write(new_cat_fn, format='ascii')

    coordlist_fn = os.path.join(stampdir, 'coordlist.txt')
    hsc.make_query_coordlist(cat, coordlist_fn, bands)
    hsc.cutout_query(coordlist_fn, outdir=stampdir)

    # give stamps more useful names
    stamp_files = [f for f in os.listdir(stampdir) if f[-4:]=='fits']
    stamp_files = sorted(stamp_files, key=lambda f: int(f.split('-')[0]))
    grouped_files = utils.grouper(stamp_files, len(bands))

    for num, files in enumerate(grouped_files):
        for i in range(len(bands)):
            old_fn = files[i]
            rerun = old_fn.split('-')[-1]
            rerun = rerun.replace('_', '-')
            new_fn = 'candy-{}-{}-{}'.format(num, bands[i].lower(), rerun)
            old_fn = os.path.join(stampdir, old_fn)
            new_fn = os.path.join(stampdir, new_fn)
            os.rename(old_fn, new_fn)
