
from __future__ import print_function

__all__ = ['runsex']

def runsex(imagefile, sexfile='default.sex', cat='hunt4udgs.cat', **kwargs):
    """
    Run sextractor and make ds9 regions file from catalog.

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
    **kwargs : dict, optional
        Any sextractor config parameter. 

    Notes
    -----
    All the sextractor configuration files must be in the
    runsex/config directory. The input files must be within 
    in a directory called sexin that is in the same directory
    as the script that calls runsex. The output from sextractor 
    will be saved in sexout, which will be created (if it 
    doesn't exist) in the run directory.
    """
    import os
    import subprocess
    from toolbox.utils import sexout_to_ds9reg

    # get the run directory and make sure sexin
    # and sexout are good to go
    rundir = os.getcwd()
    outdir = os.path.join(rundir, 'sexout')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    indir = os.path.join(rundir, 'sexin')
    assert os.path.isdir(indir), 'must have input images in sexin/'

    # run from config directory
    filedir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(filedir, 'config'))

    imfile = os.path.join(indir, imagefile)
    catfile = os.path.join(outdir, cat)
    cmd = 'sex -c '+sexfile+' '+imfile
    cmd += ' -CATALOG_NAME '+catfile

    for key, val in kwargs.iteritems():
        cmd += ' -'+key+' '+str(val)

    print('running:', '\n'+cmd+'\n')
    subprocess.call(cmd, shell=True)

    print('making ds9 regions file')
    sexout_to_ds9reg(outdir+'/'+cat)

    os.chdir(rundir)
