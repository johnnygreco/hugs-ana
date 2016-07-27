
from __future__ import print_function

import os

__all__ = ['SexWrapper']

class SexWrapper(object):
    """
    A python wrapper for SExtractor.

    Parameters
    ----------
    config : dict, optional
        Default config parameters that will remain fixed 
        within the SexWrapper instance.
    params : list, optional
        List of catalog parameters to save in addition to 
        those given in cat_params. Only used if PARAMETERS_NAME
        is not in config, which will override the this option.
    sexin: string, optional
        The input sextractor directory. Input images must
        be within this directory. If 'default', the directory
        structure is assumed to be sexin/sexpy.
    sexout: string, optional
        The input sextractor directory. Output files will
        be written to this directory, which will be created
        if it doesn't exist. If 'default', the directory structure 
        is assumed to be sexout/sexpy.
    """
    
    #################################################
    # All instances will save these parameters to a 
    # catalog. These parameters are overridden if 
    # PARAMETERS_NAME is given in config argument.
    #################################################

    cat_params = ['X_IMAGE', 'Y_IMAGE', 'ALPHA_J2000', 'DELTA_J2000', 
                  'MAG_AUTO', 'FLUX_RADIUS', 'FWHM_IMAGE', 'A_IMAGE',
                  'B_IMAGE', 'THETA_IMAGE']

    def __init__(self, config={}, params=[], sexin='default', sexout='default'):

        #################################################
        # Set default configuration for this instance
        #################################################

        self.default_config = {'PARAMETERS_NAME' : 'sexpy.params',
                               'FILTER'          : 'Y',
                               'THRESH_TYPE'     : 'RELATIVE',
                               'MAG_ZEROPOINT'   : 27.0,
                               'PIXEL_SCALE'     : 0.168,
                               'SEEING_FWHM'     : 0.7,
                               'WEIGHT_THRESH'   : 0.0,
                               'PHOT_FLUXFRAC'   : 0.5}
        for key, val in config.iteritems():
            self.default_config[key.upper()] = val
        self.reset_config()

        #################################################
        # make sure sexin and sexout are good to go
        # default structure is sex{in,out}/sexpy 
        #################################################

        self._filedir = os.path.dirname(os.path.abspath(__file__))
        self._configdir = os.path.join(self._filedir, 'config')
        assert os.path.isdir(self._configdir), '** config dir doest not exit **'
        root = os.path.dirname(self._filedir)
        self._sexin = os.path.join(root, 'sexin') if sexin=='default' else sexin
        self._sexout = os.path.join(root, 'sexout') if sexout=='default' else sexout
        assert os.path.isdir(self._sexin), '** sexin directory does not exist **'

        #################################################
        # Write the sextractor parameter file with 
        # default params plus params for this instance 
        # if not given in config argument.
        #################################################

        if 'PARAMETERS_NAME' not in config.keys():
            self.params = self.cat_params + params
            param_file = open(os.path.join(self._configdir, 'sexpy.params'), 'w')
            print('\n'.join(self.params), file=param_file)
            param_file.close()

    def reset_config(self):
        """
        Reset the sextractor config params to the defaults 
        given upon instantiation. 
        """
        self.config = self.default_config.copy()

    def get_sexin(self): 
        """
        Return the sexin input directory.
        """
        return self._sexin

    def get_sexout(self): 
        """
        Return the sexout output directory.
        """
        return self._sexout

    def set_config(self, key=None, val=None, **kwargs):
        """
        Set sextractor configuration parameter(s).

        Parameters
        ----------
        key : string 
            The param to set.
        val : string
            The value to set.
        **kwargs : dict
            Parameters and values to set. 

        Notes
        -----
        Sextractor's CHECKIMAGE config params should
        be set with the set_check_images method below.
        """
        if key is not None:
            assert val is not None
            self.config[key.upper()] = val
        for _key, _val in kwargs.iteritems():
            self.config[_key.upper()] = _val

    def set_check_images(self, which='all', prefix=''):
        """
        Set sextractor's CHECKIMAGE config params. 

        Parameters
        ----------
        which : string, optional
            The type(s) of check images to set given as
            the first letter of the image type. The options
            are 'b' ('BACKGROUND'), 'f' ('FILTERED'), 
            's' ('SEGMENTATION'), and/or 'o' ('OBJECTS').
            'all' = 'bfaso'.
        prefix : string, optional
            Prefix to add to the output image names, which 
            by default are image_type.fits
        """
        imgtypes = {'b':'BACKGROUND',
                    'f':'FILTERED',
                    'a':'APERTURES',
                    's':'SEGMENTATION',
                    'o':'OBJECTS'}
        which = which.lower()
        if which=='all':
            which = 'bfaso'
        checkimg_names = ','.join([prefix+imgtypes[w].lower()+'.fits' for w in which])
        checkimg_type = ','.join([imgtypes[w] for w in which])
        self.config['CHECKIMAGE_NAME'] = checkimg_names
        self.config['CHECKIMAGE_TYPE'] = checkimg_type

    def make_kernal(self, kern_name, size, width_param, use=True):
        """
        Make a convolution file for given kernal.

        Parameters
        ----------
        kern_name : string
            The kernal name (currently only gauss or exp).
        size : odd int
            Number of pixel in x & y directions.
        width_param : float
            The param that describes the width of the kernal in
            pixels (fwhm for gauss and scale length for exp).
        use : bool
            If True, set this kernal as the current filter.
        """
        import kernals
        kern = {'gauss':kernals.gauss, 'exp':kernals.exp}[kern_name]
        convfile = kern(size, width_param, write=True)
        if use:
            self.param['FILTER_NAME'] = convfile

    def write_config(self, fn='myconfig.sex'):
        """
        Write the current configuration file. This can be used as input 
        for sextractor, but it is actually intended for logging.

        Paramerers
        ----------
        fn : string, optional
            Config file name. 
        """
        out = open(fn, 'w')
        for key, val in self.config.iteritems():
            print('%-16s %-16s' % (key, val), file=out)
        out.close()

    def run(self, imagefile, sexfile='default.sex', cat='sex.cat', relpath=''):
        """
        Run sextractor.

        Parameters
        ----------
        imagefile : string
            Image file name. The images must be in 
            sexin directory, which should be in the
            run directory. 
        sexfile : string, optional
            Sextractor configure file name. Must be in config directory. 
            All config params set in this instance will override settings
            in this file. By default, we use sectractor's default.sex
            configuration file. 
        cat : string, optional
            Catalog name. Will be written to sexout/{relpath} directory.
        relpath : string, optional
            Relative path from within the sexin and sexout directories. 
            (See note (ii))

        Notes
        -----
         i) All the sextractor configuration files must be in the
            sexpy/config directory. 
        ii) Input files are assumed to be in sexin/{relpath}, and output files will
            be saved to sexout/{relpath}, which will be created if it doesn't exist. 
        """
        import os
        import subprocess

        # get the run directory 
        rundir = os.getcwd()

        # run from config directory
        os.chdir(self._configdir)

        # append relative path, create sexout path
        # if it doesn't exist
        indir = os.path.join(self._sexin, relpath)
        outdir = self._sexout
        relpath = [''] if relpath=='' else ['']+relpath.split('/')
        for path in relpath:
            outdir = os.path.join(outdir, path)
            if not os.path.isdir(outdir):
                print('creating', outdir)
                os.mkdir(outdir)
        assert os.path.isdir(indir)
        assert os.path.isdir(outdir)

        imfile = os.path.join(indir, imagefile)
        catfile = os.path.join(outdir, cat)
        cmd = 'sex -c '+sexfile+' '+imfile
        cmd += ' -CATALOG_NAME '+catfile

        for key, val in self.config.iteritems():
            if 'IMAGE' in key:
                if 'CHECK' not in key:
                    val = os.path.join(indir, val)
                elif key == 'CHECKIMAGE_NAME':
                    withpath = [os.path.join(outdir,v) for v in val.split(',')]
                    val = ','.join(withpath)
            cmd += ' -'+key+' '+str(val)

        print('running:', '\n'+cmd+'\n')
        subprocess.call(cmd, shell=True)

        # change back to original run directory
        os.chdir(rundir)
