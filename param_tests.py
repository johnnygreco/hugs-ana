#!/usr/bin/env python 

from sex import runsex, kernals, config
from toolbox.utils import ds9view, sexout_to_ds9reg

band = 'I'
tract = '9348'
patch = '7-6'
imfile = 'img.fits'

fwhm = 15
size = 31
convfile = kernals.gauss(size, fwhm, write=True)

config['FILTER_NAME'] = convfile

relpath = 'HSC-'+band+'/'+tract+'/'+patch[0]+'-'+patch[-1]+'/'
runsex(imfile, cat='sex.cat', relpath=relpath, make_ds9reg=True, **config)

sexin = 'sexin/'+relpath+'/'
sexout = 'sexout/'+relpath+'/'

sexout_to_ds9reg(sexout+'sex.cat', textparam='MAG_AUTO')
ds9view(sexin+imfile, sexout+'sex.reg')
