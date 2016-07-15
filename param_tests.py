#!/usr/bin/env python 

from runsex import runsex, kernals
from toolbox.utils import ds9view

#imdir = 'deepCoadd_9348_7-6_HSC-I/'
imdir = 'deepCoadd_9348_8-6_HSC-I/'

imfile = imdir+'img.fits'

alpha = 30. # ~5"/0.168"/pixel
size = 11
convfile = kernals.exp(size, alpha, write=True)

config = {'PARAMETERS_NAME' : 'myparams',
          'FILTER_NAME'     : convfile,
          'DEBLEND_NTHRESH' : 1,
          'DEBLEND_MINCONT' : 1,
          'DETECT_MINAREA'  : 5,
          'DETECT_THRESH'   : 1.5, 
          'CLEAN_PARAM'     : 0.5,
          'ANALYSIS_THRESH' : 1.5,
          'MAG_ZEROPOINT'   : 27.0, 
          'PIXEL_SCALE'     : 0.168}

runsex(imfile, **config)

ds9view('sexin/'+imfile, 'sexout/hunt4udgs.reg', mecube=True)
