#!/usr/bin/env python 

from sex import runsex, kernals, config
from toolbox.utils import ds9view

band = 'I'
tract = '9590'
patch = '1-4'

imfile = 'img.fits'

fwhm = 15
size = 31
convfile = kernals.gauss(size, fwhm, write=True)

config['FILTER_NAME'] = convfile

relpath = 'HSC-'+band+'/'+tract+'/'+patch[0]+'-'+patch[-1]+'/'
runsex(imfile, cat='sex.cat', relpath=relpath, **config)

#ds9view('sexin/'+imfile, 'sexout/'+catfile[:-4]+'.reg', mecube=True)
