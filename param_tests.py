#!/usr/bin/env python 

from runsex import runsex, kernals
from toolbox.utils import ds9view

band = 'I'
tract = '9348'
patch = '7-6'

imdir = 'deepCoadds/HSC-'+band+'/'+tract+'/'+patch+'/'

imfile = imdir+'img_x_bad.fits'

alpha = 10. 
size = 11
convfile = kernals.exp(size, alpha, write=True)

config = {'PARAMETERS_NAME' : 'myparams',
          'FILTER_NAME'     : convfile,
          'THRESH_TYPE'     : 'RELATIVE',
          'DEBLEND_NTHRESH' : 6,
          'DEBLEND_MINCONT' : 0.008,
          'DETECT_MINAREA'  : 10,
          'DETECT_THRESH'   : 2.4, 
          'ANALYSIS_THRESH' : 2.4,
          'BACK_SIZE'       : 128.0,
          'CLEAN_PARAM'     : 1,
          'MAG_ZEROPOINT'   : 27.0, 
          'PIXEL_SCALE'     : 0.168,
          'SEEING_FWHM'     : 0.7, 
          'WEIGHT_IMAGE'    : imdir+'sig.fits',
          'WEIGHT_TYPE'     : 'MAP_RMS', 
          }

catfile = 'HSC-'+band+'_'+tract+'_'+patch+'.cat'

runsex(imfile, cat=catfile, **config)

ds9view('sexin/'+imfile, 'sexout/'+catfile[:-4]+'.reg', mecube=True)
