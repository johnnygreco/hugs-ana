
from __future__ import print_function
__all__ = ['runsex']

def runsex(imagefile, config='hunt4udgs.sex', cat='hunt4udgs.cat', 
           outdir='../../data/sexout', **kwargs):
    """
    Run sextractor and make ds9 regions file from catalog.

    Parameters
    ----------
    imagefile : string
        Full path and file name to image fits file.
    config : string, optional
        Sextractor configure file name. 
        Must be in sextractor directory. 
    cat : string, optional
        Catalog name. Will be written to outdir.
    outdir :  string, optinal
        Output directory (the catalog is written here).
    **kwargs : dict, optional
        Any sextractor config parameter. 
    """
    import os
    import subprocess
    from toolbox.utils import sexout_to_ds9reg

    # run from sextractor directory
    if os.getcwd().split('/')[-1] != 'sextractor':
        os.chdir(os.getcwd()+'/sextractor')

    cmd = ['sex', '-c', config, imagefile]

    cmd.append('-CATALOG_NAME '+outdir+'/'+cat)

    for key, val in kwargs.iteritems():
        cmd.append('-'+key+' '+str(val))

    print('running:', ' '.join(cmd))
    subprocess.call(cmd)

    print('making ds9 regions file')
    sexout_to_ds9reg(outdir+'/'+cat)

    os.chdir(os.getcwd())
