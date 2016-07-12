#!/usr/bin/env python 

from sextractor import runsex
from toolbox.utils import ds9view

imfile = 'deepCoadd_HSC-I_9348_8-6.fits'

config = {'DETECT_MINAREA'  : 5,
          'DETECT_THRESH'   : 1.5, 
          'ANALYSIS_THRESH' : 1.5}

runsex(imfile, **config)

ds9view('../data/HSC/'+imfile, '../data/sexout/hunt4udgs.reg', mecube=True)
