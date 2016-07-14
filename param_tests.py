#!/usr/bin/env python 

from sextractor import runsex, kernals
from toolbox.utils import ds9view

imfile = 'deepCoadd_HSC-I_9348_8-6.fits'

alpha = 10.
size = 9
convfile = kernals.exp(size, alpha, write=True)

config = {'PARAMETERS_NAME' : 'params',
          'FILTER_NAME'     : convfile,
          'DEBLEND_NTHRESH' : 32,
          'DEBLEND_MINCONT' : 1,
          'DETECT_MINAREA'  : 5,
          'DETECT_THRESH'   : 1.5, 
          'ANALYSIS_THRESH' : 1.5}

runsex(imfile, **config)

ds9view('../data/HSC/'+imfile, '../data/sexout/hunt4udgs.reg', mecube=True)
