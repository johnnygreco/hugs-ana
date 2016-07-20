#!/usr/bin/env python 

from sex import runsex, kernals
from toolbox.utils import ds9view

band = 'I'
tract = '9616'
patch = '0-3'

imdir = 'deepCoadds/HSC-'+band+'/'+tract+'/'+patch+'/'

imfile = 'img.fits'

alpha = 5
size = 21
convfile = kernals.exp(size, alpha, write=True)

config = {'PARAMETERS_NAME' : 'myparams',
          'FILTER'          : 'Y', 
          'FILTER_NAME'     : convfile,
          'THRESH_TYPE'     : 'RELATIVE',
          'DEBLEND_NTHRESH' : 16,
          'DEBLEND_MINCONT' : 0.01,
          'DETECT_MINAREA'  : 800,
          'DETECT_THRESH'   : 1., 
          'ANALYSIS_THRESH' : 1.,
          'BACK_SIZE'       : 100.0,
          'BACK_FILTERSIZE' : 3,
          'CLEAN'           : 'Y',
          'CLEAN_PARAM'     : 0.1,
          'MAG_ZEROPOINT'   : 27.0, 
          'PIXEL_SCALE'     : 0.168,
          'SEEING_FWHM'     : 0.7, 
          'WEIGHT_IMAGE'    : 'wts_bad.fits',
          'WEIGHT_TYPE'     : 'MAP_WEIGHT', 
          'WEIGHT_THRESH'   : 0.0, 
          'PHOT_APERTURES'  : '3,4,5,6,7,8,16,32',
          'PHOT_FLUXFRAC'   : 0.5,
          'PHOT_AUTOAPERS'  : '5.0,5.0',
          'CHECKIMAGE_NAME' :'sex_bckgrd.fits,sex_filter.fits,sex_aps.fits,sex_seg.fits,sex_objs.fits',
          'CHECKIMAGE_TYPE' : 'BACKGROUND,FILTERED,APERTURES,SEGMENTATION,OBJECTS'
          }

catfile = 'sex.cat'

runsex(imfile, cat=catfile, relpath=imdir, **config)

#ds9view('sexin/'+imfile, 'sexout/'+catfile[:-4]+'.reg', mecube=True)
