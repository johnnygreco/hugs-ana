
from __future__ import print_function

__all__ = ['runsex']

def runsex(imagefile, sexfile='default.sex', cat='sex.cat',
           make_ds9reg=False, relpath='', **kwargs):
    """
    Run sextractor and option to make ds9 regions file from catalog.

    Parameters
    ----------
    imagefile : string
        Image file name. The images must be in 
        sexin directory, which should be in the
        run directory. 
    sexfile : string, optional
        Sextractor configure file name. 
        Must be in config directory. 
    cat : string, optional
        Catalog name. Will be written to sexout 
        directory in the run directory.
    make_ds9reg : bool, optional
        If True, make a ds9 regions file with the
        sextraactor catalog.
    relpath : string, optional
        Relative path from within the sexin/sexout 
        directories. See note (ii).
    **kwargs : dict, optional
        Any sextractor config parameter. 

    Notes
    -----
     i) All the sextractor configuration files must be in the
        sex/config directory. 
    ii) Input files are assumed to be in sexin/relpath, and output files will
        be saved to sexout/relpath, which will be created if it doesn't exist. 
    """
    import os
    import subprocess
    from toolbox.utils import sexout_to_ds9reg

    # get the run directory and make sure sexin
    # and sexout are good to go
    rundir = os.getcwd()

    indir = os.path.join(rundir, os.path.join('sexin', relpath))
    assert os.path.isdir(indir)

    outdir = os.path.join(rundir, 'sexout')
    assert os.path.isdir(outdir)

    # if relpath not in sexout, create it
    if relpath != '':
        for path in relpath.split('/'):
            outdir = os.path.join(outdir, path)
            if not os.path.isdir(outdir):
                print('creating', outdir)
                os.mkdir(outdir)
    
    # run from config directory
    filedir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(filedir, 'config'))

    imfile = os.path.join(indir, imagefile)
    catfile = os.path.join(outdir, cat)
    cmd = 'sex -c '+sexfile+' '+imfile
    cmd += ' -CATALOG_NAME '+catfile

    for key, val in kwargs.iteritems():
        if 'IMAGE' in key:
            if 'CHECK' not in key:
                val = os.path.join(indir, val)
            elif key == 'CHECKIMAGE_NAME':
                withpath = [os.path.join(outdir,v) for v in val.split(',')]
                val = ','.join(withpath)
        cmd += ' -'+key+' '+str(val)

    print('running:', '\n'+cmd+'\n')
    subprocess.call(cmd, shell=True)

    if make_ds9reg:
        print('making ds9 regions file')
        sexout_to_ds9reg(catfile)

    os.chdir(rundir)
