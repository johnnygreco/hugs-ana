from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
from .. import utils
hscdir = os.path.join(os.environ.get('DATA_DIR'), 'hsc')

__all__ = ['load_pointings', 'make_query_coordlist', 'cutout_query']


def load_pointings(band='i'):
    """
    Return the current HSC wide pointings in
    the given band.
    """
    from astropy.table import Table
    fn = 'ObservedWidePointings.lst'  
    fn = os.path.join(hscdir, fn)
    ra = []
    dec = []
    with open(fn) as file:
        for line in iter(file):
            data = line.split('|')
            if data[1][-1]==band:
                ra.append(float(data[2]))
                dec.append(float(data[3]))
    coords = Table([ra, dec], names=['ra', 'dec'])
    return coords


def make_query_coordlist(cat, fn='coordlist.txt', bands='GRI', 
                         size=30, rerun='s16a_wide', **kwargs):
    """
    Generate coord lists for DAS query.

    Parameters
    ----------
    cat : astropy.table.Table
        Source catalog with ra & dec columns (in degrees).
    fn : string
        Coordlist file name.
    bands : str or list
        Photometric bands to fetch. 
    size : float
        Half width and height of the postage stamps in arcsec.
    rerun : string
        HSC rerun. 
    """

    file = open(fn, 'w')

    print('#?   ra       dec        sw     sh   filter '
          'image mask variance type  rerun', file=file)
    for source in cat:
        for band in bands:
            ra, dec = source['ra'], source['dec']
            line = ' {:.7f} {:.7f} {}asec {}asec HSC-{}  true '\
                   ' true  true    coadd {}'
            print(line.format(ra, dec, size, size, band, rerun), file=file)
    file.close()


def cutout_query(coordlist, username='grecoj', outdir=None, 
                 password=None, **kwargs):
    """
    Query data base for postage-stamp images.

    Parameters
    ----------
    coordlist : string
        Coordinate list (output from make_query_coordlist).
    username : string, optional
        User name. 
    outdir : string, optional
        Output direction for cutouts. If None, will use 
        date and time label. 
    """
    try:
        from subprocess import run
    except ImportError:
        from subprocess import call as run

    if outdir is None:
        import time
        timestr = time.strftime("%Y%m%d-%H%M%S")
        outdir = os.path.join(utils.hugs_pipe_io, 'stamps_'+timestr)

    utils.mkdir_if_needed(outdir)
    url = 'https://hscdata.mtk.nao.ac.jp:4443/das_quarry/cgi-bin/quarryImage'

    if password:
        cmd = 'curl {} --form list=@{} --user {}:{}'
        cmd += ' | tar xvf - -C '+outdir
        cmd = cmd.format(url, coordlist, username, password)
        print('executing:', cmd.replace(password, '****'))
    else:
        cmd = 'curl {} --form list=@{} --user {} --insecure'
        cmd += ' | tar xvf - -C'+outdir
        cmd = cmd.format(url, coordlist, username)
        print('executing:', cmd)

    run(cmd, shell=True)
    cwd = os.getcwd()
    os.chdir(outdir)
    arch_dirs = [d for d in os.listdir('.') if d[:4]=='arch']
    if len(arch_dirs)>1:
        newest = max(arch_dirs, key=os.path.getmtime)
    else:
        newest = arch_dirs[0]
    run('mv '+newest+'/* .', shell=True)
    run('rm -r '+newest, shell=True)
    os.chdir(cwd)
