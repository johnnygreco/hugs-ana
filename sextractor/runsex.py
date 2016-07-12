
from __future__ import print_function
__all__ = ['runsex']

def runsex(imagefile, config='default.sex', cat='hunt4udgs.cat', 
           outdir='../../data/sexout', imdir='../../data/HSC/', **kwargs):
    """
    Run sextractor and make ds9 regions file from catalog.

    Parameters
    ----------
    imagefile : string
        Image file name. If imdir not given, 
        the file must be in the HSC image directory. 
    config : string, optional
        Sextractor configure file name. 
        Must be in sextractor directory. 
    cat : string, optional
        Catalog name. Will be written to outdir.
    outdir :  string, optinal
        Output directory (the catalog is written here).
    imdir : string, optional
        The image directory.
    **kwargs : dict, optional
        Any sextractor config parameter. 
    """
    import os
    import subprocess
    from toolbox.utils import sexout_to_ds9reg

    # run from sextractor directory
    if os.getcwd().split('/')[-1] != 'sextractor':
        os.chdir(os.getcwd()+'/sextractor')

    cmd = 'sex -c '+config+' '+imdir+imagefile
    cmd += ' -CATALOG_NAME '+outdir+'/'+cat

    for key, val in kwargs.iteritems():
        cmd += ' -'+key+' '+str(val)

    print('running:', cmd)
    subprocess.call(cmd, shell=True)

    print('making ds9 regions file')
    sexout_to_ds9reg(outdir+'/'+cat)

    os.chdir('..')
